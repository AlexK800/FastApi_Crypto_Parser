from pydantic import BaseModel
from typing import Optional

class CryptoCurrency(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
