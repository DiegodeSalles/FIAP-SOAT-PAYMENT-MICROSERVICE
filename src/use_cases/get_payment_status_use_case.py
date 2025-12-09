from typing import Optional
from src.domain.entities import Payment
from src.ports.repositories import PaymentRepository

class GetPaymentStatusUseCase:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    async def execute(self, payment_id: str) -> Optional[Payment]:
        return await self.repository.get_by_id(payment_id)