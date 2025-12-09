import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.domain.entities import Payment, PaymentStatus
from src.infrastructure.api.routers import get_repository, get_gateway
from src.main import app

scenarios('../features/payment.feature')

class MockGatewayImplementation:
    async def generate_qr_code(self, external_id: str, amount: float):
        return {
            "qr_data": "mock_qr_data_123",
            "qr_image_url": "http://mock.url/qr.png",
            "external_id": "ORD_MOCK_123",
            "order_id": "order_123"
        }

@pytest.fixture
def mock_repository():
    mock = AsyncMock()
    mock.create.side_effect = lambda p: p
    mock.get_all.return_value = []
    return mock

@pytest.fixture
def mock_gateway():
    return MockGatewayImplementation()

@pytest.fixture
def client(mock_repository, mock_gateway):
    app.dependency_overrides[get_repository] = lambda: mock_repository
    app.dependency_overrides[get_gateway] = lambda: mock_gateway
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@given(parsers.parse('I have a valid order with ID "{order_id}" and amount {amount:f}'), target_fixture="order_data")
def order_data(order_id, amount):
    return {"order_id": order_id, "amount": amount, "customer_id": "cust_123"}

@when('I request to create a payment', target_fixture="create_response")
def create_payment(client, order_data):
    return client.post("/api/v1/payments", json=order_data)

@then('the payment should be created successfully')
def check_created(create_response):
    assert create_response.status_code == 201

@then(parsers.parse('the payment status should be "{status}"'))
def check_status(create_response, status):
    data = create_response.json()
    assert data["status"] == status

@then('the response should contain a QR code payload')
def check_qr_code(create_response):
    data = create_response.json()
    assert "qr_code_payload" in data
    assert data["qr_code_payload"] is not None

@given(parsers.parse('a payment exists with ID "{payment_id}" and status "{status}"'))
def existing_payment(mock_repository, payment_id, status):
    payment = Payment(
        id=payment_id,
        order_id="order_existing",
        customer_id="cust_mock",
        amount=50.0,
        status=PaymentStatus(status)
    )
    mock_repository.get_by_id.return_value = payment
    mock_repository.get_by_id.side_effect = lambda pid: payment if pid == payment_id else None

@when(parsers.parse('I request the status of the payment "{payment_id}"'), target_fixture="get_response")
def get_payment_status(client, payment_id):
    return client.get(f"/api/v1/payments/{payment_id}")

@then(parsers.parse('the returned status should be "{status}"'))
def check_returned_status(get_response, status):
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["status"] == status

@given(parsers.parse('no payment exists with ID "{payment_id}"'))
def no_payment_exists(mock_repository, payment_id):
    mock_repository.get_by_id.return_value = None

@then(parsers.parse('the response status code should be {status_code:d}'))
def check_status_code(get_response, status_code):
    assert get_response.status_code == status_code

@given("multiple payments exist")
def multiple_payments(mock_repository):
    mock_repository.get_all.return_value = [
        Payment(id="1", order_id="o1", customer_id="c1", amount=10.0),
        Payment(id="2", order_id="o2", customer_id="c2", amount=20.0)
    ]

@when("I request to list all payments", target_fixture="list_response")
def list_all_payments(client):
    return client.get("/api/v1/payments")

@then("I should receive a list containing all payments")
def check_list_response(list_response):
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

@when(parsers.parse('I receive a webhook notification for "{payment_id}" with status "{status}"'), target_fixture="webhook_response")
def receive_webhook(client, payment_id, status):
    detail = "accredited" if status == "approved" else "rejected_other_reason"
    mp_status = "approved" if status == "approved" else "rejected"
    
    payload = {
        "action": "order.processed",
        "data": {
            "id": "123456",
            "external_reference": payment_id,
            "total_paid_amount": 50.0,
            "total_amount": 50.0,
            "status": mp_status,
            "status_detail": detail
        }
    }
    return client.post("/api/v1/webhook/mercadopago", json=payload)

@then(parsers.parse('the payment status should be updated to "{expected_status}"'))
def check_webhook_update(mock_repository, expected_status):
    mock_repository.update_status.assert_called()
    args = mock_repository.update_status.call_args
    assert args[0][1] == expected_status