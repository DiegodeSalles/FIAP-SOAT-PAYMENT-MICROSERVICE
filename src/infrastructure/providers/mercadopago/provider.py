import httpx
import uuid
import logging
from typing import Dict, Any
from src.ports.gateways import PaymentGateway 
from src.infrastructure.providers.mercadopago.dtos import (
    MercadoPagoPaymentRequestDTO,
    MpTransactions,
    MpPayment,
    MpConfig,
    MpQr,
    MercadoPagoPaymentResponseDTO
)

logger = logging.getLogger(__name__)

class MercadoPagoProvider(PaymentGateway):
    def __init__(self, base_url: str, access_token: str, pos_id: str):
        self.base_url = base_url
        self.access_token = access_token
        self.pos_id = pos_id
        
    async def generate_qr_code(self, external_id: str, amount: float) -> Dict[str, Any]:
        amount_str = f"{amount:.2f}"
        
        payload = MercadoPagoPaymentRequestDTO(
            type="qr",
            total_amount=amount_str,
            external_reference=external_id,
            transactions=MpTransactions(
                payments=[
                    MpPayment(amount=amount_str)
                ]
            ),
            config=MpConfig(
                qr=MpQr(
                    external_pos_id=self.pos_id,
                    mode="hybrid"
                )
            )
        )

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Idempotency-Key": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/v1/orders"
                
                logger.info(f"[MercadoPago] POST {url} Payload: {payload.model_dump_json(by_alias=True)}")
                
                response = await client.post(
                    url, 
                    json=payload.model_dump(by_alias=True), 
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code not in [200, 201]:
                    logger.error(f"[MercadoPago] Erro API: {response.text}")

                response.raise_for_status()
                
                data = response.json()
                mp_response = MercadoPagoPaymentResponseDTO(**data)
                
                return {
                    "qr_data": mp_response.type_response.qr_data,
                    "qr_image_url": "N/A", 
                    "external_id": mp_response.id,
                    "order_id": external_id
                }

            except Exception as e:
                logger.error(f"[MercadoPago] Exception: {str(e)}")
                raise Exception(f"Falha na comunicação com Mercado Pago")