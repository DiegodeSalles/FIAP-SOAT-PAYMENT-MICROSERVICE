from pydantic import BaseModel, Field, ConfigDict
from typing import List

class MpPayment(BaseModel):
    amount: str

class MpTransactions(BaseModel):
    payments: List[MpPayment]

class MpQr(BaseModel):
    external_pos_id: str = Field(..., alias="external_pos_id")
    mode: str = "hybrid"

class MpConfig(BaseModel):
    qr: MpQr

class MercadoPagoPaymentRequestDTO(BaseModel):
    type: str = "qr"
    total_amount: str = Field(..., alias="total_amount")
    external_reference: str = Field(..., alias="external_reference")
    transactions: MpTransactions
    config: MpConfig

    model_config = ConfigDict(populate_by_name=True)

class MpTypeResponse(BaseModel):
    qr_data: str = Field(..., alias="qr_data")

class MercadoPagoPaymentResponseDTO(BaseModel):
    id: str
    type_response: MpTypeResponse = Field(..., alias="type_response")