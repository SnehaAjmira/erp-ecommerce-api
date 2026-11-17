"""
validators.py

Data validation checkpoints for an ERP-to-eCommerce order and inventory sync.
Records that fail are quarantined with the reason, never silently dropped.
"""

from datetime import datetime
from decimal import Decimal
from typing import Iterable, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

VALID_STATUSES = {"NEW", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"}
VALID_CURRENCIES = {"USD", "EUR", "GBP", "CAD"}

Model = TypeVar("Model", bound=BaseModel)


class OrderRecord(BaseModel):
    """ERP order line, checked before it is sent to the eCommerce platform."""

    order_id: str = Field(min_length=1, max_length=50)
    customer_id: str = Field(min_length=1)
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0, decimal_places=2)
    order_date: datetime
    status_code: str
    currency: str = "USD"

    @field_validator("status_code", "currency", mode="before")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return str(v).strip().upper()

    @field_validator("status_code")
    @classmethod
    def check_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"unknown status '{v}'")
        return v

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v: str) -> str:
        if v not in VALID_CURRENCIES:
            raise ValueError(f"unsupported currency '{v}'")
        return v


class InventoryRecord(BaseModel):
    """ERP stock position for one SKU in one warehouse."""

    sku: str = Field(min_length=1)
    warehouse_id: str = Field(min_length=1)
    quantity_on_hand: int = Field(ge=0)
    quantity_reserved: int = Field(ge=0)
    reorder_point: Optional[int] = Field(default=None, ge=0)
    last_updated: datetime

    @model_validator(mode="after")
    def reserved_within_on_hand(self):
        if self.quantity_reserved > self.quantity_on_hand:
            raise ValueError("quantity_reserved exceeds quantity_on_hand")
        return self

    @property
    def available(self) -> int:
        return self.quantity_on_hand - self.quantity_reserved


def _first_error(exc: ValidationError) -> str:
    err = exc.errors()[0]
    field = ".".join(str(p) for p in err["loc"]) or "record"
    return f"{field}: {err['msg']}"


def validate_batch(records: Iterable[dict], model: Type[Model]) -> Tuple[List[Model], List[dict]]:
    """Split a batch into valid models and rejected rows (original row + validation_error)."""
    valid, rejected = [], []
    for row in records:
        try:
            valid.append(model(**row))
        except ValidationError as exc:
            rejected.append({**row, "validation_error": _first_error(exc)})
    return valid, rejected


def find_duplicates(keys: Iterable[tuple]) -> set:
    """Return keys that appear more than once in a batch."""
    seen, dupes = set(), set()
    for k in keys:
        (dupes if k in seen else seen).add(k)
    return dupes


def reconcile(source_count: int, target_count: int, tolerance: float = 0.0) -> dict:
    """Post-sync check: did the target receive what the source sent, within tolerance?"""
    match_rate = 1.0 if source_count == 0 and target_count == 0 else (
        target_count / source_count if source_count else 0.0)
    return {
        "source_count": source_count,
        "target_count": target_count,
        "match_rate_pct": round(100 * match_rate, 1),
        "passed": abs(1 - match_rate) <= tolerance,
    }
