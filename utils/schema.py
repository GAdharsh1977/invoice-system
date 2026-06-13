from pydantic import BaseModel, Field
from typing import Optional, List

class party(BaseModel):
    name: Optional[str] = None
    vat_id: Optional[str] = None
    country: Optional[str] = None

class Item(BaseModel):
    description: Optional[str] = None
    quantity: float = 0.0
    unit_price: float = 0.0
    line_total: float = 0.0

    unit: Optional[str] = None
    tax_rate: Optional[float] = None
    discount: Optional[float] = 0
    sku: Optional[str] = None

class TaxLine(BaseModel):
    tax_category: Optional[str] = None
    tax_rate: float = 0
    tax_amount: float = 0

class Invoice(BaseModel):
    invoice_no: Optional[str] = None
    invoice_type: Optional[str] = None

    issue_date: Optional[str] = None
    due_date: Optional[str] = None

    supplier: party
    buyer: party

    currency: Optional[str] = "EUR"
    subtotal: float = 0.0
    tax_total: float = 0.0
    grand_total: float = 0.0

    items: List[Item] = Field(default_factory=list)
    tax_lines: List[TaxLine] = Field(default_factory=list)

    source_type: Optional[str] = None
    invoice_standard: Optional[str] = None