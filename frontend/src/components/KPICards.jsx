import React, { useMemo } from "react"

const fmt2 = (n) => Number(n).toFixed(2)

export default function KPICards({ history }) {
  const kpis = useMemo(() => {
    const last = history[0]
    const avg = history.length
      ? history.reduce((acc, curr) => acc + curr.predicted_kwh, 0) / history.length
      : 0
    const max = history.length ? Math.max(...history.map((h) => h.predicted_kwh)) : 0
    return [
      { label: "Last Prediction", value: last ? `${fmt2(last.predicted_kwh)} kWh` : "—" },
      { label: "Rolling Average", value: history.length ? `${fmt2(avg)} kWh` : "—" },
      { label: "Maximum Load", value: history.length ? `${fmt2(max)} kWh` : "—" },
    ]
  }, [history])

  return (
    <div className="kpi">
      {kpis.map((k, i) => (
        <div key={i} className="kpiItem">
          <div className="kpiLabel">{k.label}</div>
          <div className="kpiValue">{k.value}</div>
        </div>
      ))}
    </div>
  )
}
