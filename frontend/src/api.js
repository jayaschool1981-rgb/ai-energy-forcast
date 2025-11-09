
const DEFAULT = "http://localhost:8000"
const base = import.meta.env.VITE_API_URL || DEFAULT

export async function predictEnergy({ timestamp, temp_c }) {
  const res = await fetch(`${base}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ timestamp, temp_c })
  })
  if (!res.ok) {
    const txt = await res.text()
    throw new Error(`API ${res.status}: ${txt}`)
  }
  return res.json()
}
