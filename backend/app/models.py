from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint
from .database import Base

class Ticker(Base):
    __tablename__ = "tickers"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True)
    category = Column(String, index=True)  # e.g., FAANG, MICRO_CAP, MEME, INDEX

class Candle(Base):
    __tablename__ = "candles"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    __table_args__ = (UniqueConstraint('symbol', 'date', name='uq_symbol_date'),)
