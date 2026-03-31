import aiohttp
import json
import asyncio
from typing import List
from datetime import datetime
import logging

from app.models.crypto import CryptoCurrency
from app.core.config import settings
from app.core.cache import get_cache, set_cache

# База данных
from app.database.base import get_session
from app.database.crud import add_price, get_history as get_history_from_db

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 1  # секунды


# =========================
# Функция для получения списка криптовалют
# =========================
async def fetch_cryptos(page: int = 1, per_page: int = 10) -> List[CryptoCurrency]:
    cache_key = f"cryptos:{page}:{per_page}"
    cached = await get_cache(cache_key)
    if cached:
        logger.info(f"Возвращаем данные из кэша: {cache_key}")
        return [CryptoCurrency(**item) for item in json.loads(cached)]

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Запрос к CoinGecko: page={page}, attempt={attempt}")
            async with aiohttp.ClientSession() as session:
                async with session.get(settings.coingecko_api_url, params=params, timeout=10) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    await set_cache(cache_key, json.dumps(data))
                    return [CryptoCurrency(**item) for item in data]
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"Ошибка запроса к CoinGecko: {e}, попытка {attempt}")
            if attempt == MAX_RETRIES:
                if cached:
                    logger.warning("Возвращаем устаревший кэш")
                    return [CryptoCurrency(**item) for item in json.loads(cached)]
                raise RuntimeError(f"Не удалось получить данные криптовалют: {e}") from e
            await asyncio.sleep(RETRY_DELAY * attempt)


# =========================
# Функция для получения истории цен из CoinGecko
# =========================
async def fetch_crypto_history(crypto_id: str, days: int = 7) -> List[dict]:
    """
    Получение истории цен криптовалюты за последние N дней.
    Сохраняет историю в Redis и PostgreSQL.
    """
    cache_key = f"history:{crypto_id}:{days}"
    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)

    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    # сохраняем только цены: [[timestamp, price], ...]
                    prices = [{"timestamp": ts, "price": price} for ts, price in data.get("prices", [])]

                    # Сохраняем в кэш Redis
                    await set_cache(cache_key, json.dumps(prices))

                    # Сохраняем в БД
                    await save_crypto_history_to_db(crypto_id, prices)

                    return prices
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"Ошибка получения истории {crypto_id}: {e}, попытка {attempt}")
            if attempt == MAX_RETRIES:
                if cached:
                    logger.warning("Возвращаем устаревший кэш истории")
                    return json.loads(cached)
                raise RuntimeError(f"Не удалось получить историю криптовалюты {crypto_id}: {e}") from e
            await asyncio.sleep(RETRY_DELAY * attempt)


# =========================
# Сохранение истории цен в PostgreSQL
# =========================
async def save_crypto_history_to_db(crypto_id: str, prices: List[dict]):
    """
    Сохраняет историю цен криптовалюты в PostgreSQL.
    """
    async for session in get_session():
        for p in prices:
            ts = datetime.utcfromtimestamp(p["timestamp"] / 1000)
            await add_price(session, crypto_id, p["price"], ts)


# =========================
# Получение истории цен из БД
# =========================
async def get_crypto_history_from_db(crypto_id: str, days: int = 7):
    """
    Возвращает историю цен из базы данных.
    """
    async for session in get_session():
        history = await get_history_from_db(session, crypto_id, days)
        return [{"timestamp": int(h.timestamp.timestamp() * 1000), "price": h.price} for h in history]
