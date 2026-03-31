# Crypto Parser API

Асинхронный FastAPI сервис для получения актуальных данных криптовалют с CoinGecko.

### Особенности Senior-ready:
- Асинхронность aiohttp
- Кэширование Redis
- Retry + обработка ошибок
- Логирование + Prometheus метрики
- Тесты на отказоустойчивость
- Docker + Docker Compose

### Запуск локально
```bash
docker-compose up --build