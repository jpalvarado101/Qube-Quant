import { useEffect, useRef, useState } from "react";
import { ColorType, createChart, type IChartApi, type ISeriesApi } from "lightweight-charts";
import {
  ingest,
  train,
  predict,
  getCandles,
  getLatestPrices,
  getTrainStatus,
  validateTicker,
  type Candle,
  type LatestPrice,
  type TrainStatus,
} from "./api";

export default function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [addTickerInput, setAddTickerInput] = useState("");
  const [result, setResult] = useState<string>("");
  const [prediction, setPrediction] = useState<{
    symbol: string;
    signal: string;
    probability?: number;
  } | null>(null);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [latest, setLatest] = useState<LatestPrice[]>([]);
  const [busy, setBusy] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string>("");
  const [statusKind, setStatusKind] = useState<"info" | "success" | "error">("info");
  const [predictError, setPredictError] = useState<string>("");
  const [trainStatus, setTrainStatus] = useState<TrainStatus | null>(null);
  const [isTraining, setIsTraining] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    if (typeof window === "undefined") return "light";
    const stored = window.localStorage.getItem("theme");
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });
  const chartContainerRef = useRef<HTMLDivElement | null>(null);
  const chartApiRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const trainPollRef = useRef<number | null>(null);

  const defaultTickers = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "NVDA",
    "GME",
    "AMC",
    "IWM",
  ];

  const [customTickers, setCustomTickers] = useState<string[]>([]);
  const [tickerNames, setTickerNames] = useState<Record<string, string>>({});
  const quickTickers = [...customTickers, ...defaultTickers];

  async function handleIngest() {
    setIsIngesting(true);
    setBusy(true);
    try {
      await ingest(defaultTickers);
      setStatusKind("success");
      setStatusMsg("Default tickers ingested.");
    } catch (e: any) {
      setStatusKind("error");
      setStatusMsg(e.message);
    } finally {
      setBusy(false);
      setIsIngesting(false);
    }
  }

  async function handleAddTicker() {
    const sym = addTickerInput.trim().toUpperCase();
    if (!sym) {
      setStatusKind("error");
      setStatusMsg("Enter a ticker symbol.");
      return;
    }
    if (!/^[A-Z0-9.\-]{1,12}$/.test(sym)) {
      setStatusKind("error");
      setStatusMsg("Ticker format looks invalid.");
      return;
    }
    if (defaultTickers.includes(sym) || customTickers.includes(sym)) {
      setStatusKind("error");
      setStatusMsg("Ticker already in the list.");
      return;
    }
    setBusy(true);
    try {
      const res = await validateTicker(sym);
      if (!res.valid) {
        setStatusKind("error");
        setStatusMsg("Ticker not found. Check the symbol and try again.");
        return;
      }
      setCustomTickers((prev) => [sym, ...prev]);
      if (res.name) {
        setTickerNames((prev) => ({ ...prev, [sym]: res.name! }));
      }
      setAddTickerInput("");
      setStatusKind("success");
      setStatusMsg(`Added ${sym} to recent tickers.`);
    } catch (e: any) {
      setStatusKind("error");
      setStatusMsg(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleTrain() {
    setBusy(true);
    setIsTraining(true);
    setTrainStatus({ status: "running", current: 0, total: 0, message: "" });
    startTrainPolling();
    train()
      .then(() => {
        setStatusKind("success");
        setStatusMsg("Training complete.");
      })
      .catch((e: any) => {
        setStatusKind("error");
        setStatusMsg(e.message);
      })
      .finally(() => {
        setBusy(false);
        setIsTraining(false);
      });
  }

  async function handlePredict(symbol?: string) {
    const sym = (symbol ?? ticker).trim().toUpperCase();
    if (!sym) {
      setPredictError("Enter a valid ticker before predicting.");
      return;
    }
    if (!/^[A-Z0-9.\-]{1,12}$/.test(sym)) {
      setPredictError("Ticker format looks invalid.");
      return;
    }
    setPredictError("");
    setBusy(true);
    try {
      const r = await predict(sym);
      setPrediction(r);
      setResult(
        `${r.symbol}: ${r.signal}${r.probability ? ` (~${r.probability.toFixed(2)})` : ""}`,
      );
      const series = await getCandles(sym, 200);
      setCandles(series);
      setStatusKind("success");
      setStatusMsg(`Predicted ${sym}.`);
    } catch (e: any) {
      setResult(e.message);
      setPredictError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleUpdateAll() {
    const symbols = [...defaultTickers, ...customTickers];
    if (symbols.length === 0) {
      setStatusKind("error");
      setStatusMsg("No tickers to update.");
      return;
    }
    setBusy(true);
    try {
      await ingest(symbols);
      await refreshLatest();
      setStatusKind("success");
      setStatusMsg(`Updated ${symbols.length} tickers.`);
    } catch (e: any) {
      setStatusKind("error");
      setStatusMsg(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function refreshLatest() {
    try {
      const data = await getLatestPrices();
      setLatest(data);
    } catch (e: any) {
      setResult(e.message);
      setStatusKind("error");
      setStatusMsg(e.message);
    }
  }

  function startTrainPolling() {
    if (trainPollRef.current != null) return;
    const poll = async () => {
      try {
        const status = await getTrainStatus();
        setTrainStatus(status);
        if (status.status !== "running") {
          if (trainPollRef.current != null) {
            window.clearInterval(trainPollRef.current);
            trainPollRef.current = null;
          }
        }
      } catch (e: any) {
        setTrainStatus({ status: "error", current: 0, total: 0, message: e.message });
        if (trainPollRef.current != null) {
          window.clearInterval(trainPollRef.current);
          trainPollRef.current = null;
        }
      }
    };
    poll();
    trainPollRef.current = window.setInterval(poll, 1000);
  }

  useEffect(() => {
    if (!chartContainerRef.current) return;
    const chart = createChart(chartContainerRef.current, {
      height: 320,
      layout: {
        textColor: "#111827",
        background: { type: ColorType.Solid, color: "#ffffff" },
      },
      grid: {
        vertLines: { color: "#f3f4f6" },
        horzLines: { color: "#f3f4f6" },
      },
      rightPriceScale: { borderColor: "#e5e7eb" },
      timeScale: { borderColor: "#e5e7eb" },
    });
    const series = chart.addCandlestickSeries({
      upColor: "#16a34a",
      downColor: "#ef4444",
      borderUpColor: "#16a34a",
      borderDownColor: "#ef4444",
      wickUpColor: "#16a34a",
      wickDownColor: "#ef4444",
    });
    chartApiRef.current = chart;
    seriesRef.current = series;

    const resize = () => {
      if (!chartContainerRef.current) return;
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };
    resize();

    const observer = new ResizeObserver(resize);
    observer.observe(chartContainerRef.current);

    return () => {
      observer.disconnect();
      chart.remove();
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current) return;
    seriesRef.current.setData(candles);
    if (chartApiRef.current) {
      chartApiRef.current.timeScale().fitContent();
    }
  }, [candles]);

  useEffect(() => {
    refreshLatest();
  }, []);

  useEffect(() => {
    return () => {
      if (trainPollRef.current != null) {
        window.clearInterval(trainPollRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    window.localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    if (!chartApiRef.current) return;
    const isDark = theme === "dark";
    chartApiRef.current.applyOptions({
      layout: {
        textColor: isDark ? "#e5e7eb" : "#111827",
        background: {
          type: ColorType.Solid,
          color: isDark ? "#0b1220" : "#ffffff",
        },
      },
      grid: {
        vertLines: { color: isDark ? "#1f2937" : "#f3f4f6" },
        horzLines: { color: isDark ? "#1f2937" : "#f3f4f6" },
      },
      rightPriceScale: { borderColor: isDark ? "#334155" : "#e5e7eb" },
      timeScale: { borderColor: isDark ? "#334155" : "#e5e7eb" },
    });
  }, [theme]);

  const signal = prediction?.signal ?? "-";
  const confidence = prediction?.probability;
  const signalColor =
    signal === "BUY" ? "#16a34a" : signal === "SELL" ? "#ef4444" : "#f59e0b";
  const confidencePct = confidence != null ? Math.round(confidence * 100) : null;
  const trainTotal = trainStatus?.total ?? 0;
  const trainCurrent = trainStatus?.current ?? 0;
  const trainPct =
    trainTotal > 0 ? Math.min(100, Math.round((trainCurrent / trainTotal) * 100)) : 0;

  return (
    <div className="min-h-screen bg-white text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-4 py-8 md:grid-cols-[1fr_minmax(0,720px)_320px]">
        <div />
        <main>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">Market Forecasting Dashboard</h1>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                Ingest historical data, train per-ticker models, and view next-day signal predictions.
              </p>
            </div>
            <button
              className="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? "Light mode" : "Dark mode"}
            </button>
          </div>

          <h1 className="mt-6 text-l font-semibold text-slate-900 dark:text-slate-100">Ingest & Training</h1>
          <div className="mt-4 flex flex-wrap items-center gap-2">
          <button
            className="rounded-lg border border-slate-200 bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white"
            disabled={busy}
            onClick={handleIngest}
          >
            {isIngesting ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/30 border-t-white dark:border-slate-900/30 dark:border-t-slate-900" />
                Ingesting...
              </span>
            ) : (
              "Ingest Default Set"
            )}
          </button>
            <input
              className="min-w-[200px] flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-slate-400 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              value={addTickerInput}
              onChange={(e) => setAddTickerInput(e.target.value)}
              placeholder="Add ticker to quick list (e.g., SHOP.TO)"
            />
            <button
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
              disabled={busy}
              onClick={handleAddTicker}
            >
              Add Ticker
            </button>
            <button
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
              disabled={busy}
              onClick={handleUpdateAll}
            >
              Update All
            </button>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <button
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
              disabled={busy}
              onClick={handleTrain}
            >
              Train
            </button>
            <div className="min-w-[220px] flex-1">
              <div className="mb-1 flex justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>
                  {isTraining
                    ? `Training ${trainCurrent}/${trainTotal || "?"}`
                    : "Training idle"}
                </span>
                <span>{isTraining ? `${trainPct}%` : ""}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                <div
                  className="h-full bg-emerald-600 transition-all"
                  style={{ width: `${isTraining ? trainPct : 0}%` }}
                />
              </div>
            </div>
          </div>

          <div
            className={
              statusKind === "success"
                ? "mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-900 dark:border-emerald-900/40 dark:bg-emerald-950/40 dark:text-emerald-200"
                : statusKind === "error"
                ? "mt-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-900 dark:border-rose-900/40 dark:bg-rose-950/40 dark:text-rose-200"
                : "mt-4 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
            }
          >
            {statusMsg || "Status: idle."}
          </div>

          <h1 className="mt-6 text-l font-semibold text-slate-900 dark:text-slate-100">Prediction</h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <input
              className="min-w-0 flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-slate-400 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="Ticker (e.g., AAPL)"
            />
            <button
              className="rounded-lg border border-slate-200 bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
              disabled={busy}
              onClick={() => handlePredict()}
            >
              Predict
            </button>
          <pre className="w-full rounded-lg bg-slate-50 p-3 text-xs text-slate-700 dark:bg-slate-900 dark:text-slate-300 md:min-w-0 md:flex-1">
            {result}
          </pre>
        </div>
        {predictError ? (
          <div className="mt-2 text-xs text-rose-600 dark:text-rose-400">
            {predictError}
          </div>
        ) : null}
          <div className="mt-6 flex items-center gap-4">
            <span
              className="rounded-full px-3 py-1 text-xs font-semibold text-white"
              style={{ background: signalColor }}
            >
              {signal}
            </span>
            <div className="flex-1">
              <div className="mb-1 flex justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>Confidence</span>
                <span>{confidencePct != null ? `${confidencePct}%` : "N/A"}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                <div
                  className="h-full"
                  style={{
                    width: `${confidencePct ?? 0}%`,
                    background: signalColor,
                  }}
                />
              </div>
            </div>
          </div>

          <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-200">
            <div>
              For educational purposes only. Not financial advice. No guarantees. Use at your own
              risk.
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-slate-200 p-3 dark:border-slate-700">
            <div className="mb-2 text-xs text-slate-500 dark:text-slate-400">
              Recent price action
            </div>
            <div ref={chartContainerRef} className="h-80 w-full" />
          </div>
        </main>

        <aside>
          <h1 className="text-l font-semibold text-slate-900 dark:text-slate-100">Recent Tickers</h1>
          <div className="mt-3 flex flex-wrap gap-2">
            {quickTickers.map((t) => (
              <button
                key={t}
                className="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                disabled={busy}
                onClick={() => {
                  setTicker(t);
                  handlePredict(t);
                }}
                title={tickerNames[t] ?? t}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="mt-6 rounded-xl border border-slate-200 p-3 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-500 dark:text-slate-400">
                Tracked tickers (latest close)
              </div>
              <button
                className="rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-700 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                disabled={busy}
                onClick={refreshLatest}
              >
                Refresh
              </button>
            </div>
            <div className="mt-3 grid gap-2">
              {latest.length === 0 ? (
                <div className="text-xs text-slate-500 dark:text-slate-400">
                  No tickers yet. Ingest data first.
                </div>
              ) : (
                latest.map((item) => (
                  <div
                    key={item.symbol}
                    className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-700"
                  >
                    <div className="font-medium text-slate-900 dark:text-slate-100">
                      {item.symbol}
                    </div>
                    <div className="text-slate-600 dark:text-slate-300">
                      {item.close.toFixed(2)}
                      <span className="ml-2 text-xs text-slate-400 dark:text-slate-500">
                        {item.date}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
