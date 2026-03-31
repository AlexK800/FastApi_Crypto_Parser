from sqlalchemy.future import select
from app.database.models import CryptoPriceHistory
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

async def add_price(session: AsyncSession, crypto_id: str, price: float, timestamp: datetime):
    new_entry = CryptoPriceHistory(crypto_id=crypto_id, price=price, timestamp=timestamp)
    session.add(new_entry)
    await session.commit()

async def get_history(session: AsyncSession, crypto_id: str, days: int = 7):
    since = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(
        select(CryptoPriceHistory)
        .where(CryptoPriceHistory.crypto_id == crypto_id)
        .where(CryptoPriceHistory.timestamp >= since)
        .order_by(CryptoPriceHistory.timestamp)
    )
    return result.scalars().all()
