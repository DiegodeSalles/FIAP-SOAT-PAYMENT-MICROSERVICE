from abc import ABC, abstractmethod
from src.domain.entities import Payment

class OrderService(ABC):

    @abstractmethod
    async def notify_payment_status(self, payment: Payment) -> None:
        pass
