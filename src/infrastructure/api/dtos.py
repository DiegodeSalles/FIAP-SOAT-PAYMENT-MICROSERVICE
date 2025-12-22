from pydantic import BaseModel, Field
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CreatePaymentRequestDTO(BaseModel):
    order_id: str = Field(..., description="Unique identifier for the order")
    customer_id: Optional[str] = Field(None, description="ID of the customer")
    amount: float = Field(..., gt=0, description="Amount to charge")

class WebhookDataDTO(BaseModel):
    id: str = Field(..., alias="id")
    external_reference: str = Field(..., alias="external_reference") 
    total_paid_amount: float = Field(..., alias="total_paid_amount")
    total_amount: float = Field(..., alias="total_amount")
    status: str
    status_detail: str = Field(..., alias="status_detail")

class WebhookRequestDTO(BaseModel):
    action: str
    data: WebhookDataDTO
    model_config = ConfigDict(populate_by_name=True)

class PaymentResponseDTO(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the payment")
    customer_id: Optional[str] = Field(None, description="Customer ID")
    amount: float = Field(..., description="Amount charged")
    order_id: str = Field(..., description="Unique identifier for the order")
    qr_code_payload: Optional[str] = Field(None, description="QR code payload")
    external_payment_id: Optional[str] = Field(None, description="Provider's payment ID")
    status: str = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(..., description="Last update timestamp")
    model_config = ConfigDict(from_attributes=True)