import type { UTCTimestamp } from 'lightweight-charts'

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

export type Candle = { time: UTCTimestamp; open: number; high: number; low: number; close: number }

export async function getCandles(symbol: string, limit = 200) {
  const res = await fetch(`${API_BASE}/predict/candles?symbol=${encodeURIComponent(symbol)}&limit=${limit}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<Candle[]>
}

export type LatestPrice = { symbol: string; date: string; close: number }

export async function getLatestPrices() {
  const res = await fetch(`${API_BASE}/predict/latest`)
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<LatestPrice[]>
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

export type ValidateResult = { symbol: string; valid: boolean; reason: string; name: string | null }

export async function validateTicker(symbol: string) {
  const res = await fetch(`${API_BASE}/ingest/validate?symbol=${encodeURIComponent(symbol)}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<ValidateResult>
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

export type TrainStatus = { status: 'idle' | 'running' | 'done' | 'error'; current: number; total: number; message: string }

export async function getTrainStatus() {
  const res = await fetch(`${API_BASE}/train/status`)
  if (!res.ok) throw new Error(await res.text())
  return res.json() as Promise<TrainStatus>
}
