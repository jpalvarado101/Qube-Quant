const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function predict(symbol: string) {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol })
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<{ symbol: string; signal: string; probability?: number }>
}

export async function ingest(symbols: string[]) {
  const today = new Date().toISOString().slice(0,10)
  const res = await fetch(`${API_BASE}/ingest/yahoo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbols, start: '2015-01-01', end: today })
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function train(symbols?: string[]) {
  const res = await fetch(`${API_BASE}/train`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbols: symbols ?? null })
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}