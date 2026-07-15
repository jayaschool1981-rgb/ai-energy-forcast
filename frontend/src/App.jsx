import React, { useEffect, useState } from "react"
import Card from "./components/Card"
import EnergyChart from "./components/EnergyChart"
import KPICards from "./components/KPICards"
import AuthGuard from "./components/AuthGuard"
import { predictEnergy, getPredictionHistory, setApiKey } from "./api"

const fmt2 = (n) => Number(n).toFixed(2)

export default function App() {
  const [timestamp, setTimestamp] = useState(() => new Date().toISOString().replace(/\.\d{3}Z$/, "Z"))
  const [temp, setTemp] = useState(25.0)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [authTrigger, setAuthTrigger] = useState(0)

  // Fetch prediction history on component mount (or authentication change)
  useEffect(() => {
    async function loadHistory() {
      if (!localStorage.getItem("X-API-Key")) return
      try {
        const hist = await getPredictionHistory()
        setHistory(hist)
      } catch (err) {
        console.error("Failed to load prediction history:", err)
        setError(err.message || "Authentication failed. Key might be invalid.")
      }
    }
    loadHistory()
  }, [authTrigger])

  async function onPredict() {
    // 1. Client-Side Input Boundary Validations
    if (!timestamp.trim()) {
      setError("Timestamp cannot be blank.")
      return
    }
    const parsedDate = Date.parse(timestamp)
    if (isNaN(parsedDate)) {
      setError("Invalid ISO 8601 Date format.")
      return
    }

    const tNum = Number(temp)
    if (isNaN(tNum) || tNum < -50 || tNum > 60) {
      setError("Temperature must be a valid number between -50°C and +60°C.")
      return
    }

    setLoading(true)
    setError("")
    try {
      const data = await predictEnergy({ timestamp, temp_c: tNum })
      setResult(data)
      // Update local history cache by prepending and maintaining top 20 logs
      setHistory((prev) => [data, ...prev].slice(0, 20))
    } catch (e) {
      setError(e.message || "An error occurred during inference call.")
    } finally {
      setLoading(false)
    }
  }

  function handleLogout() {
    setApiKey("")
    setResult(null)
    setHistory([])
    setError("")
    setAuthTrigger(prev => prev + 1)
  }

  return (
    <AuthGuard onAuthenticated={() => setAuthTrigger(prev => prev + 1)}>
      <div className="container">
        <div className="header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span className="badge">⚡ AI Energy Enterprise Forecast</span>
          <button 
            onClick={handleLogout} 
            className="input" 
            style={{ 
              width: "auto", 
              cursor: "pointer", 
              fontSize: 12, 
              padding: "4px 12px", 
              background: "rgba(255, 99, 99, 0.08)", 
              border: "1px solid rgba(255, 99, 99, 0.2)",
              color: "#ff8080"
            }}
          >
            Logout Security Session
          </button>
        </div>
        <div className="h1">Demand Forecasting Console</div>
        <div className="sub">
          Production telemetry integration powered by scikit-learn MLP regression weights.
        </div>

        <div className="grid">
          <Card title="Telemetry Settings">
            <div className="row">
              <div>
                <div className="label">Inference Target (ISO Timestamp)</div>
                <input
                  className="input"
                  value={timestamp}
                  onChange={(e) => setTimestamp(e.target.value)}
                  placeholder="2025-11-08T14:00:00Z"
                />
              </div>
              <div>
                <div className="label">Ambient Temperature (°C)</div>
                <input
                  className="input"
                  type="number"
                  step="0.1"
                  min="-50"
                  max="60"
                  value={temp}
                  onChange={(e) => setTemp(e.target.value)}
                />
              </div>
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
              <button className="button" onClick={onPredict} disabled={loading}>
                {loading ? "Inference Active…" : "Run Inference"}
              </button>
              <button
                className="input"
                style={{ width: "auto", cursor: "pointer" }}
                onClick={() => {
                  setResult(null)
                  setError("")
                  setTimestamp(new Date().toISOString().replace(/\.\d{3}Z$/, "Z"))
                }}
              >
                Reset Target
              </button>
            </div>

            {error && (
              <div style={{ color: "#ff9393", marginTop: 12, fontSize: 13, background: "rgba(255, 147, 147, 0.08)", padding: "8px 12px", borderRadius: "8px", border: "1px solid rgba(255, 147, 147, 0.25)" }}>
                ⚠️ {error}
              </div>
            )}

            <KPICards history={history} />
          </Card>

          <Card title="Active Inference Output">
            {!result ? (
              <div style={{ color: "#a1a6c3", fontSize: 13, padding: "20px 0" }}>
                Awaiting telemetry input parameters...
              </div>
            ) : (
              <div style={{ display: "grid", gap: 12, fontSize: 14 }}>
                <div style={{ padding: "8px 12px", background: "rgba(255,255,255,0.02)", borderRadius: 8 }}>
                  <strong>ISO Timestamp:</strong> <code style={{ color: "#47d0ff" }}>{result.timestamp}</code>
                </div>
                <div style={{ padding: "8px 12px", background: "rgba(255,255,255,0.02)", borderRadius: 8 }}>
                  <strong>Temperature Input:</strong> <span style={{ color: "#e6e9ff" }}>{result.temp_c} °C</span>
                </div>
                <div style={{ padding: "12px", background: "rgba(124, 138, 255, 0.12)", border: "1px solid rgba(124,138,255,0.3)", borderRadius: 8 }}>
                  <strong>Predicted Demand:</strong>{" "}
                  <span style={{ fontSize: 18, fontWeight: "bold", color: "#7c8aff" }}>
                    {fmt2(result.predicted_kwh)} kWh
                  </span>
                </div>
              </div>
            )}
          </Card>
        </div>

        <div className="grid-analytics">
          <Card title="Telemetry Logs (PostgreSQL/SQLite Mock API)">
            <div className="tableWrap" style={{ maxHeight: 220 }}>
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Temp (°C)</th>
                    <th>Forecast (kWh)</th>
                  </tr>
                </thead>
                <tbody>
                  {history.length === 0 ? (
                    <tr>
                      <td colSpan="3" style={{ textAlign: "center", color: "#a1a6c3" }}>
                        No history loaded from database.
                      </td>
                    </tr>
                  ) : (
                    history.map((h, i) => (
                      <tr key={i}>
                        <td>{h.timestamp}</td>
                        <td>{h.temp_c}</td>
                        <td style={{ fontWeight: "bold", color: "#7c8aff" }}>{fmt2(h.predicted_kwh)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <div className="footer">
              Service Endpoint: <code>{import.meta.env.VITE_API_URL || "http://localhost:8000"}</code>
            </div>
          </Card>

          <Card title="Demand Analytics (Chronological Trend)">
            <EnergyChart data={history} />
          </Card>
        </div>
      </div>
    </AuthGuard>
  )
}
