from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentGateway(ABC):
    @abstractmethod
    async def generate_qr_code(self, order_id: str, amount: float) -> Dict[str, Any]:
        pass
