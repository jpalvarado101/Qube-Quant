import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
import yfinance as yf
from .models import Base, Ticker, Price
from .db import engine

# Create tables once (safe to call)
Base.metadata.create_all(engine)

FAANG = ["META", "AAPL", "AMZN", "NFLX", "GOOGL", "MSFT", "NVDA", "TSLA"]

def fetch_and_store(session: Session, symbols=FAANG, period="15y"):
    for sym in symbols:
        t = session.execute(select(Ticker).where(Ticker.symbol==sym)).scalar_one_or_none()
        if not t:
            t = Ticker(symbol=sym, name=sym)
            session.add(t)
            session.flush()
        df = yf.download(sym, period=period, auto_adjust=False)
        df.reset_index(inplace=True)
        for _, r in df.iterrows():
            p = Price(
                ticker_id=t.id,
                date=r['Date'].date(),
                open=float(r['Open']),
                high=float(r['High']),
                low=float(r['Low']),
                close=float(r['Close']),
                adj_close=float(r['Adj Close']),
                volume=float(r['Volume'])
            )
            session.merge(p)
        session.commit()
