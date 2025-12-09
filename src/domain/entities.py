from enum import Enum
from datetime import datetime, UTC
from pydantic import ConfigDict, BaseModel, Field
from typing import Optional

class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Payment(BaseModel):
    id: str
    order_id: str
    customer_id: str
    amount: float
    status: PaymentStatus = PaymentStatus.PENDING
    qr_code_payload: Optional[str] = None
    external_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(populate_by_name=True)
