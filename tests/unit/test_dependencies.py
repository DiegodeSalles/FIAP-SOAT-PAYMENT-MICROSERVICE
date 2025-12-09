import pytest
from unittest.mock import AsyncMock, MagicMock
from src.domain.entities import Payment, PaymentStatus
from src.infrastructure.db.mongo_repository import MongoPaymentRepository

@pytest.fixture
def mock_motor_client():
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = AsyncMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.payments = mock_collection
    mock_collection.find = MagicMock()
    
    return mock_client, mock_collection

@pytest.mark.asyncio
async def test_create_payment(mock_motor_client):
    mock_client, mock_collection = mock_motor_client  
    repo = MongoPaymentRepository(mock_client, "fakedb")

    payment = Payment(id="1", order_id="o1", customer_id="c1", amount=10.0, status=PaymentStatus.PENDING)
    
    await repo.create(payment)
    
    mock_collection.insert_one.assert_called_once()
    call_args = mock_collection.insert_one.call_args[0][0]
    assert call_args["_id"] == "1"

@pytest.mark.asyncio
async def test_get_by_id_found(mock_motor_client):
    mock_client, mock_collection = mock_motor_client
    
    mock_collection.find_one.return_value = {
        "_id": "1", "order_id": "o1", "customer_id": "c1", "amount": 10.0, "status": "pending"
    }
    
    repo = MongoPaymentRepository(mock_client, "fakedb")
    result = await repo.get_by_id("1")
    
    assert result is not None
    assert result.id == "1"

@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_motor_client):
    mock_client, mock_collection = mock_motor_client
    mock_collection.find_one.return_value = None
    
    repo = MongoPaymentRepository(mock_client, "fakedb")
    result = await repo.get_by_id("999")
    
    assert result is None

@pytest.mark.asyncio
async def test_get_by_external_id_found(mock_motor_client):
    mock_client, mock_collection = mock_motor_client
    mock_collection.find_one.return_value = {
        "_id": "1", "order_id": "o1", "customer_id": "c1", "amount": 10.0, "status": "pending",
        "external_payment_id": "ext_123"
    }
    
    repo = MongoPaymentRepository(mock_client, "fakedb")
    result = await repo.get_by_external_id("ext_123")
    
    assert result is not None
    assert result.id == "1"
    mock_collection.find_one.assert_called_with({"external_payment_id": "ext_123"})

@pytest.mark.asyncio
async def test_get_all(mock_motor_client):
    mock_client, mock_collection = mock_motor_client

    async def async_cursor_generator():
        data = [
            {"_id": "1", "order_id": "o1", "customer_id": "c1", "amount": 10.0, "status": "pending"},
            {"_id": "2", "order_id": "o2", "customer_id": "c2", "amount": 20.0, "status": "approved"}
        ]
        for item in data:
            yield item

    mock_collection.find.return_value = async_cursor_generator()
    
    repo = MongoPaymentRepository(mock_client, "fakedb")
    results = await repo.get_all()
    
    assert len(results) == 2
    assert results[0].id == "1"

@pytest.mark.asyncio
async def test_update_status(mock_motor_client):
    mock_client, mock_collection = mock_motor_client
    
    mock_collection.find_one.return_value = {
        "_id": "1", "order_id": "o1", "customer_id": "c1", "amount": 10.0, "status": "approved"
    }

    repo = MongoPaymentRepository(mock_client, "fakedb")
    result = await repo.update_status("1", PaymentStatus.APPROVED)
    
    mock_collection.update_one.assert_called_once()
    assert result.status == PaymentStatus.APPROVED