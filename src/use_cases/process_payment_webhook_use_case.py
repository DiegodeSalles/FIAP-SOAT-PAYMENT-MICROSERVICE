from typing import Optional
from src.domain.entities import Payment, PaymentStatus
from src.ports.repositories import PaymentRepository
from src.infrastructure.api.dtos import WebhookRequestDTO

class ProcessPaymentWebhookUseCase:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    async def execute(self, webhook_data: WebhookRequestDTO) -> Optional[Payment]:
        payment_id = webhook_data.data.external_reference        
        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            return None

        new_status = PaymentStatus.PENDING
        
        if webhook_data.action == "order.processed" and webhook_data.data.status_detail == "accredited":
            new_status = PaymentStatus.APPROVED
            payment.amount = webhook_data.data.total_paid_amount
        elif webhook_data.action == "payment.created": 
             return payment
        else:
            new_status = PaymentStatus.REJECTED

        updated_payment = await self.repository.update_status(payment.id, new_status)
        return updated_payment