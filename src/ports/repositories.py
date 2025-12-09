from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities import Payment, PaymentStatus

class PaymentRepository(ABC):
    @abstractmethod
    async def create(self, payment: Payment) -> Payment:
        pass

    @abstractmethod
    async def get_by_id(self, payment_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    async def get_by_external_id(self, external_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    async def update_status(self, payment_id: str, status: PaymentStatus, external_id: Optional[str] = None) -> Optional[Payment]:
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        pass