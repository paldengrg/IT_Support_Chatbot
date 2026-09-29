from pydantic import BaseModel


class License(BaseModel):
    product: str
    aliases: list[str] = []
    vendor: str
    price_per_user_year: float
    currency: str
    available: bool
    requires_approval: bool
    renewal: str
    purchase_process: str
