from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.models.crypto import CryptoCurrency
from app.services.crypto_service import (
    fetch_cryptos,
    fetch_crypto_history,
    get_crypto_history_from_db
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/crypto", tags=["crypto"])


# =========================
# GET /crypto/ – список криптовалют с пагинацией
# =========================
@router.get("/", response_model=List[CryptoCurrency])
async def get_cryptos(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page")
):
    logger.info(f"API запрос /crypto?page={page}&per_page={per_page}")
    return await fetch_cryptos(page=page, per_page=per_page)


# =========================
# GET /crypto/{crypto_id} – детальная информация по одной криптовалюте
# =========================
@router.get("/{crypto_id}", response_model=CryptoCurrency)
async def get_crypto_detail(crypto_id: str):
    logger.info(f"API запрос /crypto/{crypto_id}")
    cryptos = await fetch_cryptos(page=1, per_page=250)
    crypto = next((c for c in cryptos if c.id == crypto_id), None)
    if not crypto:
        raise HTTPException(status_code=404, detail="Crypto not found")
    return crypto


# =========================
# GET /crypto/search/ – поиск по имени или символу
# =========================
@router.get("/search/", response_model=List[CryptoCurrency])
async def search_crypto(query: str = Query(..., description="Имя или символ криптовалюты")):
    logger.info(f"API запрос /crypto/search?query={query}")
    cryptos = await fetch_cryptos(page=1, per_page=250)
    results = [
        c for c in cryptos
        if query.lower() in c.name.lower() or query.lower() in c.symbol.lower()
    ]
    return results


# =========================
# GET /crypto/{crypto_id}/history – история цен (prod-ready)
# =========================
@router.get("/{crypto_id}/history")
async def get_crypto_history(crypto_id: str, days: int = Query(7, ge=1, le=365)):
    """
    Возвращает историю цен криптовалюты за последние N дней.
    Сначала проверяет PostgreSQL, если данных нет — обращается к CoinGecko.
    """
    logger.info(f"API запрос /crypto/{crypto_id}/history?days={days}")

    # 1️⃣ Пытаемся получить данные из базы
    db_history = await get_crypto_history_from_db(crypto_id, days)
    if db_history and len(db_history) > 0:
        logger.info(f"Возвращаем историю из базы для {crypto_id}")
        return {"crypto_id": crypto_id, "history": db_history}

    # 2️⃣ Если данных нет или их мало, идём к CoinGecko
    try:
        history = await fetch_crypto_history(crypto_id, days)
        logger.info(f"История получена с CoinGecko и сохранена: {crypto_id}")
        return {"crypto_id": crypto_id, "history": history}
    except RuntimeError as e:
        logger.error(f"Не удалось получить историю криптовалюты {crypto_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
