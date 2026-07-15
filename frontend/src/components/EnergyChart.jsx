import React, { useState } from "react"

const fmt2 = (n) => Number(n).toFixed(2)

export default function EnergyChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div style={{ color: "#a1a6c3", textAlign: "center", padding: "48px 0", fontSize: 13 }}>
        No historical telemetry points available to render chart.
      </div>
    )
  }

  // Sort chronologically
  const sorted = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))

  const width = 500
  const height = 220
  const padding = 40

  const kwhValues = sorted.map((d) => d.predicted_kwh)
  const minKwh = Math.min(...kwhValues) * 0.95
  const maxKwh = Math.max(...kwhValues) * 1.05
  const range = maxKwh - minKwh || 1

  const points = sorted.map((d, i) => {
    const x = padding + (i / (sorted.length - 1 || 1)) * (width - 2 * padding)
    const y = height - padding - ((d.predicted_kwh - minKwh) / range) * (height - 2 * padding)
    return { x, y, val: d.predicted_kwh, temp: d.temp_c, time: d.timestamp }
  })

  let pathD = ""
  if (points.length > 0) {
    pathD = `M ${points[0].x} ${points[0].y} ` + points.slice(1).map((p) => `L ${p.x} ${p.y}`).join(" ")
  }

  const [hovered, setHovered] = useState(null)

  return (
    <div style={{ position: "relative", width: "100%" }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        height="auto"
        style={{
          background: "rgba(255, 255, 255, 0.01)",
          borderRadius: "12px",
          border: "1px solid rgba(255, 255, 255, 0.06)",
        }}
      >
        {/* Horizontal Y grid lines and labels */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
          const y = padding + ratio * (height - 2 * padding)
          const val = maxKwh - ratio * range
          return (
            <g key={idx}>
              <line
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke="rgba(255, 255, 255, 0.06)"
                strokeDasharray="4,4"
              />
              <text x={padding - 8} y={y + 3} fill="#a1a6c3" fontSize="9" textAnchor="end">
                {val.toFixed(1)}
              </text>
            </g>
          )
        })}

        {/* Path Line */}
        {points.length > 1 && (
          <path
            d={pathD}
            fill="none"
            stroke="url(#chartGradient)"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Data points */}
        {points.map((p, idx) => (
          <circle
            key={idx}
            cx={p.x}
            cy={p.y}
            r={hovered && hovered.idx === idx ? 6.5 : 4}
            fill={hovered && hovered.idx === idx ? "#47d0ff" : "#7c8aff"}
            stroke="#0f1226"
            strokeWidth="1.5"
            style={{ cursor: "pointer", transition: "all 0.15s ease" }}
            onMouseEnter={() => setHovered({ ...p, idx })}
            onMouseLeave={() => setHovered(null)}
          />
        ))}

        {/* Chart Gradients definitions */}
        <defs>
          <linearGradient id="chartGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#7c8aff" />
            <stop offset="100%" stopColor="#47d0ff" />
          </linearGradient>
        </defs>
      </svg>

      {/* Dynamic HTML Tooltip */}
      {hovered && (
        <div
          style={{
            position: "absolute",
            left: `${(hovered.x / width) * 100}%`,
            top: `${(hovered.y / height) * 100 - 15}%`,
            transform: "translate(-50%, -100%)",
            background: "rgba(21, 24, 59, 0.95)",
            border: "1px solid rgba(124, 138, 255, 0.35)",
            borderRadius: "8px",
            padding: "6px 10px",
            boxShadow: "0 8px 16px rgba(0,0,0,0.5)",
            zIndex: 10,
            fontSize: "11px",
            whiteSpace: "nowrap",
            pointerEvents: "none",
            color: "#e6e9ff",
            backdropFilter: "blur(6px)",
          }}
        >
          <div style={{ color: "#47d0ff", fontWeight: "bold" }}>{hovered.val.toFixed(2)} kWh</div>
          <div>Temp: {hovered.temp}°C</div>
          <div style={{ fontSize: "9px", color: "#a1a6c3", marginTop: "3px" }}>
            {new Date(hovered.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </div>
        </div>
      )}
    </div>
  )
}
