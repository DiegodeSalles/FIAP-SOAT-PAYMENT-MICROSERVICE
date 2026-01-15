import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.infrastructure.api import routers
from src.use_cases.get_payment_status_use_case import GetPaymentStatusUseCase
from src.use_cases.process_payment_webhook_use_case import ProcessPaymentWebhookUseCase
from src.use_cases.create_payment_use_case import CreatePaymentUseCase
from src.use_cases.get_payment_by_order_use_case import GetPaymentByOrderUseCase
from src.infrastructure.services.order_service_http import OrderServiceHTTP
from src.infrastructure.db.mongo_repository import MongoPaymentRepository
from src.infrastructure.providers.mercadopago.provider import MercadoPagoProvider
from src.domain.entities import Payment, PaymentStatus
from src.main import app

@patch('src.infrastructure.api.routers.settings')
def test_missing_dependencies_factories(mock_settings):
    mock_repo = MagicMock()
    mock_order_service = MagicMock(spec=OrderServiceHTTP)

    status_uc = routers.get_status_use_case(mock_repo)
    assert isinstance(status_uc, GetPaymentStatusUseCase)
    
    webhook_uc = routers.get_webhook_use_case(mock_repo, mock_order_service)
    assert isinstance(webhook_uc, ProcessPaymentWebhookUseCase)

@pytest.mark.asyncio
async def test_list_payments_endpoint():
    mock_repo = AsyncMock()
    mock_repo.get_all.return_value = [
        MagicMock(id="1", amount=10.0, status="pending"),
        MagicMock(id="2", amount=20.0, status="approved")
    ]
    
    result = await routers.list_payments(repo=mock_repo)
    
    assert len(result) == 2
    mock_repo.get_all.assert_called_once()

@pytest.mark.asyncio
async def test_get_payment_found():
    mock_use_case = AsyncMock()
    payment = Payment(id="123", order_id="ord1", customer_id="cust1", amount=100.0, status=PaymentStatus.PENDING)
    mock_use_case.execute.return_value = payment
    
    result = await routers.get_payment(payment_id="123", use_case=mock_use_case)
    
    assert result == payment
    mock_use_case.execute.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_get_payment_not_found():
    from fastapi import HTTPException
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await routers.get_payment(payment_id="123", use_case=mock_use_case)
    
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_get_payment_by_order_found():
    mock_use_case = AsyncMock()
    payment = Payment(id="123", order_id="ord1", customer_id="cust1", amount=100.0, status=PaymentStatus.APPROVED)
    mock_use_case.execute.return_value = payment
    
    result = await routers.get_payment_by_order(order_id="ord1", use_case=mock_use_case)
    
    assert result == payment
    mock_use_case.execute.assert_called_once_with("ord1")

@pytest.mark.asyncio
async def test_get_payment_by_order_not_found():
    from fastapi import HTTPException
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await routers.get_payment_by_order(order_id="ord1", use_case=mock_use_case)
    
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_create_payment():
    from src.infrastructure.api.dtos import CreatePaymentRequestDTO
    mock_use_case = AsyncMock()
    payment = Payment(id="123", order_id="ord1", customer_id="cust1", amount=100.0, status=PaymentStatus.PENDING)
    mock_use_case.execute.return_value = payment
    
    request = CreatePaymentRequestDTO(order_id="ord1", amount=100.0, customer_id="cust1")
    result = await routers.create_payment(request=request, use_case=mock_use_case)
    
    assert result == payment
    mock_use_case.execute.assert_called_once_with("ord1", 100.0, "cust1")

@patch('src.infrastructure.api.routers.get_repository')
@patch('src.infrastructure.api.routers.get_gateway')
@patch('src.infrastructure.api.routers.get_order_service')
def test_get_create_payment_use_case(mock_get_order_service, mock_get_gateway, mock_get_repository):
    mock_repo = MagicMock()
    mock_gateway = MagicMock()
    
    mock_get_repository.return_value = mock_repo
    mock_get_gateway.return_value = mock_gateway
    
    result = routers.get_create_payment_use_case(mock_repo, mock_gateway)
    
    assert isinstance(result, CreatePaymentUseCase)

@patch('src.infrastructure.api.routers.get_repository')
def test_get_payment_by_order_use_case(mock_get_repository):
    mock_repo = MagicMock()
    mock_get_repository.return_value = mock_repo
    
    result = routers.get_payment_by_order_use_case(mock_repo)
    
    assert isinstance(result, GetPaymentByOrderUseCase)

@patch('src.infrastructure.api.routers.settings')
@patch('src.infrastructure.api.routers.MongoDBConnection')
def test_get_repository(mock_mongo_connection, mock_settings):
    mock_settings.mongodb_db_name = "test_db"
    mock_client = MagicMock()
    mock_mongo_connection.get_client.return_value = mock_client
    
    result = routers.get_repository()
    
    assert isinstance(result, MongoPaymentRepository)
    mock_mongo_connection.get_client.assert_called_once()

@patch('src.infrastructure.api.routers.settings')
def test_get_gateway(mock_settings):
    mock_settings.mp_base_url = "https://api.mercadopago.com"
    mock_settings.mp_access_token = "test_token"
    mock_settings.mp_pos_id = "test_pos"
    
    result = routers.get_gateway()
    
    assert isinstance(result, MercadoPagoProvider)

@patch('src.infrastructure.api.routers.settings')
def test_get_order_service(mock_settings):
    mock_settings.order_status_url = "http://localhost/orders"
    
    result = routers.get_order_service()
    
    assert isinstance(result, OrderServiceHTTP)