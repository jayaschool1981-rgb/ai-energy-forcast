import os
import time
import logging
import asyncio
import collections
from datetime import datetime, timezone
from functools import lru_cache
from typing import List
from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from fastapi.security import APIKeyHeader
from fastapi.concurrency import run_in_threadpool

from src.utils import make_feature_row, SecureMLPRegressor
from api.database import init_db, save_prediction, get_history

# -------------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger("api")

# -------------------------------------------------------
# REDIS CACHE & RATE LIMIT STORE
# -------------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL")
redis_client = None
if REDIS_URL:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        logger.info("Successfully connected to Redis cache store.")
    except Exception as err:
        logger.error(f"Failed to connect to Redis at {REDIS_URL}: {err}")

# -------------------------------------------------------
# API KEY AUTHENTICATION
# -------------------------------------------------------
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
VALID_API_KEY = os.getenv("API_KEY", "enterprise-telemetry-token-2026")

def get_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key != VALID_API_KEY:
        logger.warning("Unauthorized API access attempt detected.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key security header."
        )
    return api_key

# -------------------------------------------------------
# SECURE MODEL LOADING (NPZ weights, no pickle RCE)
# -------------------------------------------------------
WEIGHTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "energy_mlp_weights.npz"))
try:
    model = SecureMLPRegressor(WEIGHTS_PATH)
    logger.info("Successfully loaded Secure MLP Regressor weights (NPZ).")
except Exception as err:
    logger.critical(f"Failed to load secure model weights: {err}")
    raise err

# -------------------------------------------------------
# MEMORY-SAFE BACKGROUND RATE LIMIT CLEANER
# -------------------------------------------------------
RATE_LIMIT_MAX = 60  # max requests
RATE_LIMIT_WINDOW = 60  # window in seconds
rate_limit_records = {}  # IP -> deque of timestamps

async def prune_inactive_ips_task():
    """Periodic task to prune expired IPs and prevent memory leaks."""
    while True:
        try:
            await asyncio.sleep(60)
            now = time.time()
            expired_ips = []
            for ip, record in list(rate_limit_records.items()):
                while record and now - record[0] >= RATE_LIMIT_WINDOW:
                    record.popleft()
                if not record:
                    expired_ips.append(ip)
            for ip in expired_ips:
                rate_limit_records.pop(ip, None)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in rate limit cleaner task: {e}")

# -------------------------------------------------------
# LIVENESS & LIFESPAN MANAGEMENT
# -------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup initialization
    init_db()
    loop = asyncio.get_running_loop()
    cleaner_task = loop.create_task(prune_inactive_ips_task())
    yield
    # Shutdown cleaning
    cleaner_task.cancel()

# -------------------------------------------------------
# RATE LIMITER (Redis with local memory fallback)
# -------------------------------------------------------
def rate_limiter(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # 1. Try Redis Rate Limiting
    if redis_client:
        try:
            key = f"rate_limit:{ip}"
            pipe = redis_client.pipeline()
            pipe.zadd(key, {str(now): now})
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.expire(key, RATE_LIMIT_WINDOW)
            _, _, count, _ = pipe.execute()
            
            if count > RATE_LIMIT_MAX:
                logger.warning(f"Redis rate limit exceeded for IP: {ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Maximum 60 requests per minute."
                )
            return
        except redis.RedisError as err:
            logger.error(f"Redis rate limiting failed, falling back to memory: {err}")
            
    # 2. Fallback to Memory-Safe Limiter
    record = rate_limit_records.setdefault(ip, collections.deque())
    while record and now - record[0] >= RATE_LIMIT_WINDOW:
        record.popleft()
        
    if len(record) >= RATE_LIMIT_MAX:
        logger.warning(f"Memory rate limit exceeded for IP: {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 60 requests per minute."
        )
    record.append(now)

# -------------------------------------------------------
# RESILIENT DUAL-LAYER CACHING WORKFLOW
# -------------------------------------------------------
@lru_cache(maxsize=1024)
def _get_cached_prediction_local(timestamp_iso: str, temp_c: float) -> float:
    # Make feature row and predict
    row = make_feature_row(timestamp_iso, temp_c)
    X = [[row["hour"], row["dayofweek"], row["month"], row["temp_c"]]]
    yhat = model.predict(X)[0]
    return float(yhat)

async def get_cached_prediction(timestamp_iso: str, temp_c: float) -> float:
    cache_key = f"prediction:{timestamp_iso}:{temp_c}"
    
    # 1. Check Redis Cache
    if redis_client:
        try:
            val = redis_client.get(cache_key)
            if val is not None:
                return float(val)
        except redis.RedisError as err:
            logger.error(f"Redis cache read error: {err}")
            
    # 2. Local Fallback Cache
    yhat = await run_in_threadpool(_get_cached_prediction_local, timestamp_iso, temp_c)
    
    # 3. Populate Redis Cache
    if redis_client:
        try:
            redis_client.setex(cache_key, 3600, str(yhat))
        except redis.RedisError as err:
            logger.error(f"Redis cache write error: {err}")
            
    return yhat

# -------------------------------------------------------
# SCHEMAS
# -------------------------------------------------------
class PredictIn(BaseModel):
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp (e.g. 2025-11-08T14:00:00Z)")
    temp_c: float = Field(..., ge=-50.0, le=60.0, description="Ambient temperature in Celsius")

    @field_validator("timestamp")
    @classmethod
    def validate_iso_timestamp(cls, v):
        try:
            # Check ISO 8601 parsing directly with datetime (no Pandas overhead!)
            val = v.replace("Z", "+00:00")
            dt = datetime.fromisoformat(val)
            return dt.isoformat().replace("+00:00", "Z")
        except Exception:
            raise ValueError("Timestamp must be a valid ISO 8601 formatted datetime string.")

class PredictOut(BaseModel):
    timestamp: str
    temp_c: float
    predicted_kwh: float

class HistoryOut(BaseModel):
    timestamp: str
    temp_c: float
    predicted_kwh: float

# -------------------------------------------------------
# APPLICATION INITIALIZATION
# -------------------------------------------------------
app = FastAPI(
    title="AI Energy Forecasting Enterprise API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS SETUP: Read allowed origins from env or default
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# GLOBAL EXCEPTION SHIELDING
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled system exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Telemetry has been flagged."}
    )

# -------------------------------------------------------
# ROUTER SETUP
# -------------------------------------------------------
v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "healthy", "model_loaded": model is not None}

@v1_router.post(
    "/predict",
    response_model=PredictOut,
    dependencies=[Depends(rate_limiter), Depends(get_api_key)],
    status_code=status.HTTP_200_OK
)
async def predict(inp: PredictIn):
    start_time = time.time()
    try:
        # Offload prediction calculation to worker thread to keep event loop responsive
        yhat = await get_cached_prediction(inp.timestamp, inp.temp_c)
        
        # Save prediction result to SQLAlchemy connection pool
        await run_in_threadpool(save_prediction, inp.timestamp, inp.temp_c, yhat)
        
        duration = time.time() - start_time
        logger.info(f"Prediction successful temp={inp.temp_c}°C duration={duration:.4f}s")
        
        return PredictOut(
            timestamp=inp.timestamp,
            temp_c=inp.temp_c,
            predicted_kwh=yhat
        )
    except Exception as e:
        logger.error(f"Prediction processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run model inference."
        )

@v1_router.get(
    "/history",
    response_model=List[HistoryOut],
    dependencies=[Depends(get_api_key)],
    status_code=status.HTTP_200_OK
)
async def prediction_history():
    try:
        history = await run_in_threadpool(get_history, 20)
        return [HistoryOut(**item) for item in history]
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query prediction logs."
        )

app.include_router(v1_router)
