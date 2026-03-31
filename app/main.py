from fastapi import FastAPI
from app.api.endpoints.crypto import router as crypto_router

app = FastAPI(title="Crypto Parser API", version="1.0")

app.include_router(crypto_router)
