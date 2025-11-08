
import React, { useEffect, useMemo, useState } from "react"
import Card from "./components/Card"
import { predictEnergy } from "./api"

const fmt2 = (n) => Number(n).toFixed(2)

export default function App() {
  const [timestamp, setTimestamp] = useState(() => new Date().toISOString())
  const [temp, setTemp] = useState(28)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const kpis = useMemo(() => {
    const last = history[history.length - 1]
    const avg = history.length
      ? history.reduce((a, b) => a + b.predicted_kwh, 0) / history.length
      : 0
    const max = history.length
      ? Math.max(...history.map(h => h.predicted_kwh))
      : 0
    return [
      { label: "Last kWh", value: last ? fmt2(last.predicted_kwh) : "—" },
      { label: "Avg kWh", value: history.length ? fmt2(avg) : "—" },
      { label: "Max kWh", value: history.length ? fmt2(max) : "—" },
    ]
  }, [history])

  async function onPredict() {
    setLoading(true)
    setError("")
    try {
      const data = await predictEnergy({ timestamp, temp_c: Number(temp) })
      setResult(data)
      setHistory(h => [...h.slice(-9), data])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <span className="badge">⚡ AI Energy Forecast</span>
      </div>
      <div className="h1">Hourly Consumption Prediction</div>
      <div className="sub">
        Predict building electricity usage from a timestamp and ambient temperature.
      </div>

      <div className="grid">
        <Card title="Input">
          <div className="row">
            <div>
              <div className="label">Timestamp (ISO)</div>
              <input
                className="input"
                value={timestamp}
                onChange={(e) => setTimestamp(e.target.value)}
              />
            </div>
            <div>
              <div className="label">Temperature (°C)</div>
              <input
                className="input"
                type="number"
                step="0.1"
                value={temp}
                onChange={(e) => setTemp(e.target.value)}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: 12, marginTop: 14 }}>
            <button className="button" onClick={onPredict} disabled={loading}>
              {loading ? "Predicting…" : "Predict"}
            </button>
            <button
              className="input"
              onClick={() => {
                setHistory([])
                setResult(null)
                setError("")
              }}
            >
              Reset
            </button>
          </div>

          {error && (
            <div style={{ color: "#ff9393", marginTop: 10, fontSize: 13 }}>
              {error}
            </div>
          )}

          <div className="kpi">
            {kpis.map((k, i) => (
              <div key={i} className="kpiItem">
                <div className="kpiLabel">{k.label}</div>
                <div className="kpiValue">{k.value}</div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Prediction">
          {!result ? (
            <div style={{ color: "#a1a6c3" }}>No prediction yet.</div>
          ) : (
            <div style={{ display: "grid", gap: 8 }}>
              <div><strong>Timestamp:</strong> {result.timestamp}</div>
              <div><strong>Temp:</strong> {result.temp_c} °C</div>
              <div><strong>Predicted:</strong> {fmt2(result.predicted_kwh)} kWh</div>
            </div>
          )}
        </Card>
      </div>

      <div style={{ marginTop: 18 }}>
        <Card title="Recent Predictions">
          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Temp (°C)</th>
                  <th>Predicted kWh</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i}>
                    <td>{h.timestamp}</td>
                    <td>{h.temp_c}</td>
                    <td>{fmt2(h.predicted_kwh)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="footer">
            API: <code>{import.meta.env.VITE_API_URL || "http://localhost:8000"}</code>
          </div>
        </Card>
      </div>
    </div>
  )
}
