import os
import unittest
from fastapi.testclient import TestClient

# Set mock env variables and disable CORS blocking for test
os.environ["ALLOWED_ORIGINS"] = "*"
os.environ["API_KEY"] = "enterprise-telemetry-token-2026"
from api.main import app, rate_limit_records

client = TestClient(app)

class TestEnergyForecastingAPI(unittest.TestCase):
    
    def setUp(self):
        # Clear local rate limiter memory before each test
        rate_limit_records.clear()
        self.headers = {"X-API-Key": "enterprise-telemetry-token-2026"}

    def test_01_health_check(self):
        # Health check is public (unauthenticated)
        response = client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy", "model_loaded": True})

    def test_02_predict_valid_input(self):
        payload = {
            "timestamp": "2025-11-08T14:00:00Z",
            "temp_c": 28.5
        }
        response = client.post("/api/v1/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["timestamp"], "2025-11-08T14:00:00Z")
        self.assertEqual(data["temp_c"], 28.5)
        self.assertIn("predicted_kwh", data)
        self.assertIsInstance(data["predicted_kwh"], float)

    def test_03_predict_invalid_temperature_bounds(self):
        # Test temperature too low
        response_low = client.post("/api/v1/predict", json={
            "timestamp": "2025-11-08T14:00:00Z",
            "temp_c": -55.0
        }, headers=self.headers)
        self.assertEqual(response_low.status_code, 422)

        # Test temperature too high
        response_high = client.post("/api/v1/predict", json={
            "timestamp": "2025-11-08T14:00:00Z",
            "temp_c": 65.0
        }, headers=self.headers)
        self.assertEqual(response_high.status_code, 422)

    def test_04_predict_invalid_date_format(self):
        payload = {
            "timestamp": "not-a-valid-date-string",
            "temp_c": 22.0
        }
        response = client.post("/api/v1/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 422)

    def test_05_get_history(self):
        # Insert a predictive log row
        client.post("/api/v1/predict", json={
            "timestamp": "2025-11-08T15:00:00Z",
            "temp_c": 22.0
        }, headers=self.headers)
        
        response = client.get("/api/v1/history", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]["temp_c"], 22.0)

    def test_06_rate_limiting(self):
        payload = {
            "timestamp": "2025-11-08T14:00:00Z",
            "temp_c": 25.0
        }
        # Run 60 requests successfully
        for _ in range(60):
            response = client.post("/api/v1/predict", json=payload, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            
        # 61st request triggers rate limiter
        response = client.post("/api/v1/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 429)
        self.assertIn("Rate limit exceeded", response.json()["detail"])

    def test_07_unauthorized_access(self):
        # Predict endpoint without auth header
        response = client.post("/api/v1/predict", json={
            "timestamp": "2025-11-08T14:00:00Z",
            "temp_c": 25.0
        })
        self.assertEqual(response.status_code, 401)
        
        # History endpoint without auth header
        response_hist = client.get("/api/v1/history")
        self.assertEqual(response_hist.status_code, 401)

    def test_08_secure_model_matches_pickle(self):
        import joblib
        from src.utils import SecureMLPRegressor
        
        # Load the original model pickle
        pickle_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "energy_mlp.pkl"))
        weights_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "energy_mlp_weights.npz"))
        if not os.path.exists(pickle_path):
            self.skipTest("Original pickle model not found.")
            
        original_model = joblib.load(pickle_path)
        secure_model = SecureMLPRegressor(weights_path)
        
        # Make a mock feature set (hour, dayofweek, month, temp_c)
        X_mock = [[14, 5, 11, 28.5]]
        
        y_pickle = original_model.predict(X_mock)[0]
        y_secure = secure_model.predict(X_mock)[0]
        
        # Assert they are equal up to 5 decimal places
        self.assertAlmostEqual(y_pickle, y_secure, places=5)

if __name__ == "__main__":
    unittest.main()
