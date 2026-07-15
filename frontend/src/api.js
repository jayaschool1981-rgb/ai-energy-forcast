const DEFAULT = "http://localhost:8000"
const base = import.meta.env.VITE_API_URL || DEFAULT

let cachedApiKey = localStorage.getItem("X-API-Key") || ""

export function setApiKey(key) {
  cachedApiKey = key
  if (key) {
    localStorage.setItem("X-API-Key", key)
  } else {
    localStorage.removeItem("X-API-Key")
  }
}

export function getApiKey() {
  return cachedApiKey
}

export function hasApiKey() {
  return !!cachedApiKey
}

export async function predictEnergy({ timestamp, temp_c }) {
  const res = await fetch(`${base}/api/v1/predict`, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "X-API-Key": cachedApiKey || ""
    },
    body: JSON.stringify({ timestamp, temp_c })
  })
  
  if (!res.ok) {
    const txt = await res.text()
    let errorMsg = `API Error (${res.status})`
    try {
      const parsed = JSON.parse(txt)
      if (parsed.detail) {
        if (Array.isArray(parsed.detail)) {
          errorMsg = parsed.detail.map(d => d.msg || d).join(", ")
        } else {
          errorMsg = parsed.detail
        }
      }
    } catch {
      errorMsg = txt || errorMsg
    }
    throw new Error(errorMsg)
  }
  return res.json()
}

export async function getPredictionHistory() {
  const res = await fetch(`${base}/api/v1/history`, {
    method: "GET",
    headers: {
      "X-API-Key": cachedApiKey || ""
    }
  })
  if (!res.ok) {
    const txt = await res.text()
    throw new Error(`API History Error ${res.status}: ${txt}`)
  }
  return res.json()
}
