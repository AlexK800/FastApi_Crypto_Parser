from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class CryptoPriceHistory(Base):
    __tablename__ = "crypto_price_history"

    id = Column(Integer, primary_key=True, index=True)
    crypto_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    price = Column(Float)
