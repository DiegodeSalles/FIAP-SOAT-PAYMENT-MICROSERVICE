from fastapi import APIRouter, Depends, HTTPException, status
from src.infrastructure.api.dtos import PaymentResponseDTO, CreatePaymentRequestDTO
from src.infrastructure.providers.mercadopago.provider import MercadoPagoProvider
from src.infrastructure.db.mongo_repository import MongoPaymentRepository
from src.infrastructure.db.mongo_client import MongoDBConnection
from src.use_cases.create_payment_use_case import CreatePaymentUseCase
from src.use_cases.get_payment_by_order_use_case import GetPaymentByOrderUseCase
from src.use_cases.process_payment_webhook_use_case import ProcessPaymentWebhookUseCase
from src.use_cases.get_payment_status_use_case import GetPaymentStatusUseCase
from src.ports.gateways import PaymentGateway
from src.infrastructure.services.order_service_http import OrderServiceHTTP
from src.config import settings

def get_repository():
    client = MongoDBConnection.get_client()
    return MongoPaymentRepository(client, settings.mongodb_db_name)

def get_gateway() -> PaymentGateway:
    return MercadoPagoProvider(
        base_url=settings.mp_base_url,
        access_token=settings.mp_access_token,
        pos_id=settings.mp_pos_id
    )

def get_order_service() -> OrderServiceHTTP:
    return OrderServiceHTTP(base_url=settings.order_status_url)

def get_create_payment_use_case(
    repo: MongoPaymentRepository = Depends(get_repository),
    gateway: PaymentGateway = Depends(get_gateway)
) -> CreatePaymentUseCase:
    return CreatePaymentUseCase(repo, gateway)

def get_status_use_case(
    repo: MongoPaymentRepository = Depends(get_repository)
) -> GetPaymentStatusUseCase:
    return GetPaymentStatusUseCase(repo)

def get_webhook_use_case(
    repo: MongoPaymentRepository = Depends(get_repository),
    order_service: OrderServiceHTTP = Depends(get_order_service)
) -> ProcessPaymentWebhookUseCase:
    return ProcessPaymentWebhookUseCase(repo, order_service)

def get_payment_by_order_use_case(
    repo: MongoPaymentRepository = Depends(get_repository)
) -> GetPaymentByOrderUseCase:
    return GetPaymentByOrderUseCase(repo)


router_payment = APIRouter(prefix="/payments", tags=["payments"])

@router_payment.post("/", response_model=PaymentResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: CreatePaymentRequestDTO,
    use_case: CreatePaymentUseCase = Depends(get_create_payment_use_case)
):
    return await use_case.execute(request.order_id, request.amount, request.customer_id)

@router_payment.get("/", response_model=list[PaymentResponseDTO])
async def list_payments(
    repo: MongoPaymentRepository = Depends(get_repository)
):
    payments = await repo.get_all()
    return payments

@router_payment.get("/{payment_id}", response_model=PaymentResponseDTO)
async def get_payment(
    payment_id: str,
    use_case: GetPaymentStatusUseCase = Depends(get_status_use_case)
):
    payment = await use_case.execute(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router_payment.get("/order/{order_id}", response_model=PaymentResponseDTO)
async def get_payment_by_order(
    order_id: str,
    use_case: GetPaymentByOrderUseCase = Depends(get_payment_by_order_use_case)
):
    payment = await use_case.execute(order_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment