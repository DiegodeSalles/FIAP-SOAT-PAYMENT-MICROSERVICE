import httpx
from src.config import settings
from src.domain.entities import Payment, PaymentStatus
from src.ports.service import OrderService

class OrderServiceHTTP(OrderService):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def notify_payment_status(self, payment: Payment) -> None:
        status_id = 2 if payment.status == PaymentStatus.APPROVED else 7
        async with httpx.AsyncClient() as client:
            await client.patch(
                settings.order_status_url,
                json={
                    "status_id": status_id,
                    "id": payment.order_id,
                },
                timeout=5.0
            )
