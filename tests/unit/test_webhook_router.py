import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.infrastructure.api.webhook_router import get_repository, get_order_service, get_webhook_use_case, receive_webhook
from src.infrastructure.db.mongo_repository import MongoPaymentRepository
from src.infrastructure.services.order_service_http import OrderServiceHTTP
from src.use_cases.process_payment_webhook_use_case import ProcessPaymentWebhookUseCase
from src.domain.entities import Payment, PaymentStatus
from src.infrastructure.api.dtos import WebhookRequestDTO, WebhookDataDTO
import pytest


class TestWebhookRouter:
    def test_get_repository(self):
        with patch('src.infrastructure.api.webhook_router.MongoDBConnection') as mock_mongo:
            with patch('src.infrastructure.api.webhook_router.settings') as mock_settings:
                mock_settings.mongodb_db_name = "test_db"
                mock_client = MagicMock()
                mock_mongo.get_client.return_value = mock_client
                
                result = get_repository()
                
                assert isinstance(result, MongoPaymentRepository)
                mock_mongo.get_client.assert_called_once()
    
    def test_get_order_service(self):
        with patch('src.infrastructure.api.webhook_router.settings') as mock_settings:
            mock_settings.order_status_url = "http://localhost/orders"
            
            result = get_order_service()
            
            assert isinstance(result, OrderServiceHTTP)
    
    def test_get_webhook_use_case(self):
        mock_repo = MagicMock()
        mock_order_service = MagicMock()
        
        result = get_webhook_use_case(mock_repo, mock_order_service)
        
        assert isinstance(result, ProcessPaymentWebhookUseCase)
    
    @pytest.mark.asyncio
    async def test_receive_webhook_not_found(self):
        from fastapi import HTTPException
        
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = None
        
        webhook_dto = WebhookRequestDTO(
            action="order.processed",
            data=WebhookDataDTO(
                id="123",
                external_reference="ext_123",
                total_paid_amount=100.0,
                total_amount=100.0,
                status="approved",
                status_detail="accredited"
            )
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await receive_webhook(webhook_dto, mock_use_case)
        
        assert exc_info.value.status_code == 404
        assert "Payment not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_receive_webhook_success(self):
        mock_use_case = AsyncMock()
        payment = Payment(id="123", order_id="ord1", customer_id="cust1", amount=100.0, status=PaymentStatus.APPROVED)
        mock_use_case.execute.return_value = payment
        
        webhook_dto = WebhookRequestDTO(
            action="order.processed",
            data=WebhookDataDTO(
                id="123",
                external_reference="ext_123",
                total_paid_amount=100.0,
                total_amount=100.0,
                status="approved",
                status_detail="accredited"
            )
        )
        
        result = await receive_webhook(webhook_dto, mock_use_case)
        
        assert result["status"] == "received"
        assert result["new_status"] == PaymentStatus.APPROVED


class TestMainApp:
    def test_main_imports_app(self):
        from src.main import app
        
        assert app is not None
        assert hasattr(app, 'dependency_overrides')
