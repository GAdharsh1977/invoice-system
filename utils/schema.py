from pydantic import BaseModel
from typing import Optional, List

class Item(BaseModel):
    name: str
    price: float
    qty: float

class Invoice(BaseModel):
    invoice_no: str
    vendor: str
    date: Optional[str]
    total: float
    currency: Optional[str] = "INR"
    items: List[Item]
    source_type: str
    status: str = "pending"
