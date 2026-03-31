import pytest
from aioresponses import aioresponses
from app.services.crypto_service import fetch_cryptos

@pytest.mark.asyncio
async def test_retry_on_failure():
    with aioresponses() as m:
        m.get("https://api.coingecko.com/api/v3/coins/markets", status=500)
        with pytest.raises(RuntimeError):
            await fetch_cryptos()
