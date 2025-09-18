from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint

Base = declarative_base()

class Ticker(Base):
    __tablename__ = "tickers"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True, unique=True)
    name = Column(String)

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(Float)
    __table_args__ = (UniqueConstraint('ticker_id', 'date', name='_ticker_date_uc'),)

class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, index=True)
    date = Column(Date, index=True)
    rsi_14 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    ret_1d = Column(Float)
    ret_5d = Column(Float)
    vol_atr = Column(Float)
    __table_args__ = (UniqueConstraint('ticker_id', 'date', name='_feat_ticker_date_uc'),)

class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, index=True)
    date = Column(Date, index=True)
    action = Column(Integer)  # 0=SELL, 1=HOLD, 2=BUY
    horizon_days = Column(Integer)
    threshold = Column(Float)
    __table_args__ = (UniqueConstraint('ticker_id', 'date', 'horizon_days', 'threshold', name='_label_uc'),)

class ModelMeta(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    model_type = Column(String)          # e.g., xgboost_classifier
    horizon_days = Column(Integer)
    threshold = Column(Float)
    path = Column(String)                # serialized file path
