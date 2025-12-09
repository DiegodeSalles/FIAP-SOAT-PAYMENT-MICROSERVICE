import uuid
from src.domain.entities import Payment, PaymentStatus
from src.ports.repositories import PaymentRepository
from src.ports.gateways import PaymentGateway

class CreatePaymentUseCase:
    def __init__(self, repository: PaymentRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    async def execute(self, order_id: str, amount: float, customer_id: str) -> Payment:
        payment_id = str(uuid.uuid4())
        gateway_response = await self.gateway.generate_qr_code(payment_id, amount)
        payment = Payment(
            id=payment_id,
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            status=PaymentStatus.PENDING,
            qr_code_payload=gateway_response.get("qr_data"),
            external_payment_id=gateway_response.get("external_id")
        )

        saved_payment = await self.repository.create(payment)
        return saved_payment