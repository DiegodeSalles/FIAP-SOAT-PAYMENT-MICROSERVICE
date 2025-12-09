import pytest
import asyncio
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import AsyncMock, patch, MagicMock
from src.infrastructure.providers.mercadopago.provider import MercadoPagoProvider
from src.infrastructure.db.mongo_repository import MongoPaymentRepository
from src.domain.entities import Payment

scenarios('../features/infrastructure.feature')

def run_async(coroutine):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

@pytest.fixture
def mp_provider():
    return MercadoPagoProvider("http://mock.api", "token", "pos_id")

@given("I have the Mercado Pago Provider configured")
def setup_provider(mp_provider):
    pass

@when(parsers.parse('I request a QR Code for order "{order_id}" with amount {amount:f}'), target_fixture="qr_result")
def call_generate_qr(mp_provider, order_id, amount):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "ORD123",
            "type_response": {"qr_data": "qr_123"}
        }
        mock_post.return_value = mock_response
        
        return run_async(mp_provider.generate_qr_code(order_id, amount))

@then("the provider should call the Mercado Pago API")
def check_api_call():
    pass

@then("return the correct QR data")
def check_qr_result(qr_result):
    assert qr_result["qr_data"] == "qr_123"
    assert qr_result["external_id"] == "ORD123"

@pytest.fixture
def mongo_repo():
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = AsyncMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.payments = mock_collection
    mock_collection.insert_one = AsyncMock()

    repo = MongoPaymentRepository(mock_client, "test_db")
    return repo

@given("I have the Mongo Repository configured")
def setup_repo(mongo_repo):
    pass

@when(parsers.parse('I save a payment with ID "{payment_id}"'), target_fixture="saved_payment")
def save_payment(mongo_repo, payment_id):
    payment = Payment(
        id=payment_id,
        order_id="ord_1",
        customer_id="cust_1",
        amount=10.0
    )
    run_async(mongo_repo.create(payment))
    return payment

@then("the repository should insert the document into the database")
def check_insert(mongo_repo, saved_payment):
    mongo_repo.collection.insert_one.assert_called_once()
    args = mongo_repo.collection.insert_one.call_args[0][0]
    assert args["_id"] == saved_payment.id