import React, { useState } from "react"
import { setApiKey } from "../api"

export default function AuthGuard({ children, onAuthenticated }) {
  const [keyInput, setKeyInput] = useState("")
  const [error, setError] = useState("")
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem("X-API-Key")
  })

  function handleLogin(e) {
    e.preventDefault()
    if (!keyInput.trim()) {
      setError("API Access Key is required.")
      return
    }
    setApiKey(keyInput.trim())
    setIsAuthenticated(true)
    if (onAuthenticated) onAuthenticated()
  }

  if (isAuthenticated) {
    return children
  }

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "70vh",
      padding: "20px"
    }}>
      <div className="card" style={{ maxWidth: 420, width: "100%", padding: 24 }}>
        <div className="cardTitle" style={{ fontSize: 18, textAlign: "center", marginBottom: 8, color: "#e6e9ff" }}>
          🔑 Access Token Required
        </div>
        <p style={{ color: "#a1a6c3", fontSize: 13, textAlign: "center", marginBottom: 20, lineHeight: "1.4" }}>
          Inference telemetry logs are secure. Please enter the valid token to authorize this session.
        </p>
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: 16 }}>
            <div className="label">X-API-Key Header Value</div>
            <input
              type="password"
              className="input"
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
              placeholder="e.g. enterprise-telemetry-token-2026"
              style={{ width: "100%" }}
            />
          </div>
          {error && (
            <div style={{ color: "#ff9393", fontSize: 12, marginBottom: 16, background: "rgba(255, 147, 147, 0.08)", padding: "8px 12px", borderRadius: 8, border: "1px solid rgba(255,147,147,0.2)" }}>
              ⚠️ {error}
            </div>
          )}
          <button type="submit" className="button" style={{ width: "100%" }}>
            Authorize Console
          </button>
        </form>
      </div>
    </div>
  )
}
