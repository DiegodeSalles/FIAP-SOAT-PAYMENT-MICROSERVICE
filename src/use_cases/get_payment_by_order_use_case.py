from typing import Optional
from src.domain.entities import Payment
from src.ports.repositories import PaymentRepository

class GetPaymentByOrderUseCase:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    async def execute(self, order_id: str) -> Optional[Payment]:
        return await self.repository.get_by_order_id(order_id)