import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.infrastructure.api.dtos import WebhookRequestDTO
from src.infrastructure.db.mongo_repository import MongoPaymentRepository
from src.infrastructure.db.mongo_client import MongoDBConnection
from src.infrastructure.services.order_service_http import OrderServiceHTTP
from src.use_cases.process_payment_webhook_use_case import ProcessPaymentWebhookUseCase
from src.config import settings

router_webhook = APIRouter(prefix="/webhook", tags=["webhook"])
logger = logging.getLogger(__name__)

def get_repository():
    client = MongoDBConnection.get_client()
    db_name = settings.mongodb_db_name
    return MongoPaymentRepository(client, db_name)

def get_order_service() -> OrderServiceHTTP:
    return OrderServiceHTTP(
        base_url=settings.order_status_url
)

def get_webhook_use_case(
    repo: MongoPaymentRepository = Depends(get_repository),
    order_service: OrderServiceHTTP = Depends(get_order_service),
) -> ProcessPaymentWebhookUseCase:
    return ProcessPaymentWebhookUseCase(repo, order_service)

@router_webhook.post("/", status_code=status.HTTP_200_OK)
async def receive_webhook(
    request: WebhookRequestDTO,
    use_case: ProcessPaymentWebhookUseCase = Depends(get_webhook_use_case)
):
    logger.info(f"[Webhook] Recebido: {request.model_dump_json()}")
    
    updated_payment = await use_case.execute(request)
    
    if not updated_payment:
        logger.error(f"[Webhook] Pagamento não encontrado: {request.data.external_reference}")
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {"status": "received", "new_status": updated_payment.status}