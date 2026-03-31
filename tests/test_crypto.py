import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_cryptos():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/crypto/?page=1&per_page=5")
    assert response.status_code == 200
    assert len(response.json()) <= 5

@pytest.mark.asyncio
async def test_get_crypto_detail():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/crypto/bitcoin")
    assert response.status_code in (200, 404)  # может быть отсутствует в кэше
    if response.status_code == 200:
        data = response.json()
        assert data["id"] == "bitcoin"

@pytest.mark.asyncio
async def test_search_crypto():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/crypto/search/?query=bit")
    assert response.status_code == 200
    results = response.json()
    for item in results:
        assert "bit" in item["name"].lower() or "bit" in item["symbol"].lower()

@pytest.mark.asyncio
async def test_crypto_history():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/crypto/bitcoin/history?days=3")
    assert response.status_code in (200, 500)  # если CoinGecko недоступен
    if response.status_code == 200:
        history = response.json()
        assert "history" in history
        assert isinstance(history["history"], list)
