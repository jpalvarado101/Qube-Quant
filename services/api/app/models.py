from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, PrimaryKeyConstraint
from .db import Base


class Price(Base):
    __tablename__ = "prices"
    symbol = Column(String, nullable=False)
    ts = Column(DateTime, nullable=False)
    o = Column(Float); h = Column(Float); l = Column(Float); c = Column(Float); v = Column(Float)
    __table_args__ = (PrimaryKeyConstraint('symbol','ts', name='pk_prices'),)


class News(Base):
    __tablename__ = "news"
    symbol = Column(String, nullable=False)
    ts = Column(DateTime, nullable=False)
    source = Column(String)
    headline = Column(String)
    url = Column(String)
    sentiment = Column(Float) # [-1,1]
    p_pos = Column(Float); p_neg = Column(Float)
    __table_args__ = (PrimaryKeyConstraint('symbol','ts','headline', name='pk_news'),)


class Feature(Base):
    __tablename__ = "features"
    symbol = Column(String, nullable=False)
    ts = Column(DateTime, nullable=False)
    rsi = Column(Float); macd = Column(Float); atr = Column(Float); vol = Column(Float)
    sent_agg = Column(Float)
    __table_args__ = (PrimaryKeyConstraint('symbol','ts', name='pk_features'),)


class Run(Base):
    __tablename__ = "runs"
    id = Column(String, primary_key=True)
    status = Column(String)
    algo = Column(String)
    params_json = Column(JSON)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    metrics_json = Column(JSON)


class Signal(Base):
    __tablename__ = "signals"
    run_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    ts = Column(DateTime, nullable=False)
    action = Column(Integer) # 0 hold, 1 buy, 2 sell
    confidence = Column(Float)
    price = Column(Float)
    pnl_1d = Column(Float)
    pnl_5d = Column(Float)
    __table_args__ = (PrimaryKeyConstraint('run_id','symbol','ts', name='pk_signals'),)