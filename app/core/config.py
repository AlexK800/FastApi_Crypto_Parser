from fastapi import APIRouter, Query
from typing import List
from app.models.crypto import CryptoCurrency
from app.services.crypto_service import fetch_cryptos
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/crypto", tags=["crypto"])

@router.get("/", response_model=List[CryptoCurrency])
async def get_cryptos(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page")
):
    logger.info(f"API запрос /crypto?page={page}&per_page={per_page}")
    return await fetch_cryptos(page=page, per_page=per_page)
