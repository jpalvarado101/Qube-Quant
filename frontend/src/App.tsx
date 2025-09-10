import { useState } from 'react'
import { ingest, train, predict } from './api'

export default function App() {
  const [ticker, setTicker] = useState('AAPL')
  const [result, setResult] = useState<string>('')
  const [busy, setBusy] = useState(false)

  async function handleIngest() {
    setBusy(true)
    try {
      await ingest(['AAPL','MSFT','GOOGL','AMZN','META','TSLA','NVDA','GME','AMC','IWM'])
      alert('Ingested!')
    } catch (e:any) { alert(e.message) } finally { setBusy(false) }
  }

  async function handleTrain() {
    setBusy(true)
    try {
      await train()
      alert('Trained!')
    } catch (e:any) { alert(e.message) } finally { setBusy(false) }
  }

  async function handlePredict() {
    setBusy(true)
    try {
      const r = await predict(ticker.trim().toUpperCase())
      setResult(`${r.symbol}: ${r.signal}${r.probability ? ` (p≈${r.probability.toFixed(2)})` : ''}`)
    } catch (e:any) { setResult(e.message) } finally { setBusy(false) }
  }

  return (
    <div style={{ maxWidth: 640, margin: '40px auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <h1>Stock Signal (Buy / Hold / Sell)</h1>
      <p>Demo app. Start by ingesting data, then training, then predicting.</p>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button disabled={busy} onClick={handleIngest}>Ingest Default Set</button>
        <button disabled={busy} onClick={handleTrain}>Train</button>
      </div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <input value={ticker} onChange={e=>setTicker(e.target.value)} placeholder="Ticker (e.g., AAPL)" />
        <button disabled={busy} onClick={handlePredict}>Predict</button>
      </div>
      <pre style={{ marginTop: 24, background: '#f9fafb', padding: 12, borderRadius: 8 }}>{result}</pre>
    </div>
  )
}
