
import React from "react"

export default function Card({ title, children, footer }) {
  return (
    <div className="card">
      {title && <div className="cardTitle">{title}</div>}
      <div>{children}</div>
      {footer && <div style={{ marginTop: 12 }}>{footer}</div>}
    </div>
  )
}
