import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.infrastructure.db.mongo_client import MongoDBConnection
from src.infrastructure.services.order_service_http import OrderServiceHTTP
from src.infrastructure.db.mongo_repository import MongoPaymentRepository
from src.infrastructure.providers.mercadopago.provider import MercadoPagoProvider
from src.domain.entities import Payment, PaymentStatus
from src.config import get_settings
from src.ports.repositories import PaymentRepository
from src.ports.gateways import PaymentGateway
from src.ports.service import OrderService
from src.use_cases.get_payment_by_order_use_case import GetPaymentByOrderUseCase


class TestMongoDBConnection:
    @patch('src.infrastructure.db.mongo_client.AsyncIOMotorClient')
    def test_get_client_creates_client(self, mock_motor_client):
        MongoDBConnection.client = None
        
        mock_client_instance = MagicMock()
        mock_motor_client.return_value = mock_client_instance
        
        with patch('src.infrastructure.db.mongo_client.settings') as mock_settings:
            mock_settings.mongodb_url = "mongodb://localhost:27017"
            
            client = MongoDBConnection.get_client()
            
            assert client == mock_client_instance
            mock_motor_client.assert_called_once()
    
    @patch('src.infrastructure.db.mongo_client.AsyncIOMotorClient')
    def test_get_client_returns_existing_client(self, mock_motor_client):
        mock_client_instance = MagicMock()
        MongoDBConnection.client = mock_client_instance
        
        client = MongoDBConnection.get_client()
        
        assert client == mock_client_instance
        mock_motor_client.assert_not_called()


class TestOrderServiceHTTP:
    @pytest.mark.asyncio
    @patch('src.infrastructure.services.order_service_http.httpx.AsyncClient')
    async def test_notify_payment_status_approved(self, mock_async_client):
        base_url = "http://localhost:8000"
        service = OrderServiceHTTP(base_url=base_url)
        
        mock_client_instance = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        payment = Payment(id="123", order_id="ord1", customer_id="cust1", amount=100.0, status=PaymentStatus.APPROVED)
        
        with patch('src.infrastructure.services.order_service_http.settings') as mock_settings:
            mock_settings.order_url = "http://order-service/status"
            
            await service.notify_payment_status(payment)
            
            mock_client_instance.patch.assert_called_once()
            call_args = mock_client_instance.patch.call_args
            assert call_args[1]['json']['status_id'] == 2
            assert call_args[1]['json']['id'] == "ord1"
    
    @pytest.mark.asyncio
    @patch('src.infrastructure.services.order_service_http.httpx.AsyncClient')
    async def test_notify_payment_status_rejected(self, mock_async_client):
        base_url = "http://localhost:8000"
        service = OrderServiceHTTP(base_url=base_url)
        
        mock_client_instance = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        payment = Payment(id="123", order_id="ord1", customer_id="cust1", amount=100.0, status=PaymentStatus.REJECTED)
        
        with patch('src.infrastructure.services.order_service_http.settings') as mock_settings:
            mock_settings.order_url = "http://order-service/status"
            
            await service.notify_payment_status(payment)
            
            mock_client_instance.patch.assert_called_once()
            call_args = mock_client_instance.patch.call_args
            assert call_args[1]['json']['status_id'] == 7


class TestGetSettings:
    def test_get_settings_returns_settings_instance(self):
        with patch('src.config.Settings') as mock_settings_class:
            mock_instance = MagicMock()
            mock_settings_class.return_value = mock_instance
            
            get_settings.cache_clear()
            result = get_settings()
            
            assert result == mock_instance


class TestAbstractRepositories:
    def test_payment_repository_is_abstract(self):
        """Verify PaymentRepository is abstract and cannot be instantiated"""
        with pytest.raises(TypeError):
            PaymentRepository()
    
    def test_payment_gateway_is_abstract(self):
        """Verify PaymentGateway is abstract and cannot be instantiated"""
        with pytest.raises(TypeError):
            PaymentGateway()
    
    def test_order_service_is_abstract(self):
        """Verify OrderService is abstract and cannot be instantiated"""
        with pytest.raises(TypeError):
            OrderService()


class TestGetPaymentByOrderUseCase:
    @pytest.mark.asyncio
    async def test_execute_found(self):
        mock_repo = AsyncMock()
        payment = Payment(id="123", order_id="ord1", customer_id="cust1", amount=100.0, status=PaymentStatus.PENDING)
        mock_repo.get_by_order_id.return_value = payment
        
        use_case = GetPaymentByOrderUseCase(mock_repo)
        result = await use_case.execute("ord1")
        
        assert result == payment
        mock_repo.get_by_order_id.assert_called_once_with("ord1")
    
    @pytest.mark.asyncio
    async def test_execute_not_found(self):
        mock_repo = AsyncMock()
        mock_repo.get_by_order_id.return_value = None
        
        use_case = GetPaymentByOrderUseCase(mock_repo)
        result = await use_case.execute("ord1")
        
        assert result is None
        mock_repo.get_by_order_id.assert_called_once_with("ord1")


class TestMercadoPagoProvider:
    @pytest.mark.asyncio
    @patch('src.infrastructure.providers.mercadopago.provider.httpx.AsyncClient')
    async def test_generate_qr_code_success(self, mock_async_client):
        base_url = "https://api.mercadopago.com"
        access_token = "test_token"
        pos_id = "test_pos"
        
        provider = MercadoPagoProvider(base_url=base_url, access_token=access_token, pos_id=pos_id)
        
        mock_client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "test_id",
            "type_response": {
                "qr_data": "test_qr_data"
            }
        }
        mock_response.status_code = 201
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await provider.generate_qr_code("order123", 100.0)
        
        assert result["qr_data"] == "test_qr_data"
        assert result["order_id"] == "order123"
        mock_client_instance.post.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.infrastructure.providers.mercadopago.provider.httpx.AsyncClient')
    async def test_generate_qr_code_error(self, mock_async_client):
        base_url = "https://api.mercadopago.com"
        access_token = "test_token"
        pos_id = "test_pos"
        
        provider = MercadoPagoProvider(base_url=base_url, access_token=access_token, pos_id=pos_id)
        
        mock_client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_response.raise_for_status.side_effect = Exception("400 Bad Request")
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(Exception) as exc_info:
            await provider.generate_qr_code("order123", 100.0)
        
        assert "Falha na comunicação" in str(exc_info.value)


class TestMongoRepository:
    @pytest.mark.asyncio
    async def test_get_all_empty(self):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = AsyncMock()
        
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find.return_value.to_list.return_value = []
        
        repo = MongoPaymentRepository(mock_client, "test_db")
        result = await repo.get_all()
        
        assert result == []
