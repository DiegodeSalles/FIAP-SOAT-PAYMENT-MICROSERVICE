import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from src.main import app
from src.domain.entities import Payment, PaymentStatus
from src.infrastructure.api.webhook_router import get_repository, get_order_service
from unittest.mock import AsyncMock

scenarios('../features/webhook.feature')

@pytest.fixture
def mock_repository():
    mock = AsyncMock()
    async def update_side_effect(pid, status, ext_id=None):
        return Payment(
            id=pid, 
            order_id="order_1", 
            customer_id="cust_1", 
            amount=10.0, 
            status=status
        )
    mock.update_status.side_effect = update_side_effect
    mock.get_by_id.return_value = Payment(
        id="123", order_id="o1", customer_id="c1", amount=10.0
    )
    return mock

@pytest.fixture
def mock_order_service():
    mock = AsyncMock()
    mock.notify_payment_status.return_value = None
    return mock

@pytest.fixture
def client(mock_repository, mock_order_service):
    app.dependency_overrides[get_repository] = lambda: mock_repository
    app.dependency_overrides[get_order_service] = lambda: mock_order_service
    
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@given(parsers.parse('a payment exists with ID "{payment_id}" and status "{status}"'))
def existing_payment(mock_repository, payment_id, status):
    payment = Payment(
        id=payment_id,
        order_id="order_1",
        customer_id="cust_1",
        amount=10.0,
        status=PaymentStatus(status)
    )
    mock_repository.get_by_id.return_value = payment

@given(parsers.parse('no payment exists with ID "{payment_id}"'))
def no_payment(mock_repository, payment_id):
    mock_repository.get_by_id.return_value = None

@when(parsers.parse('I receive a webhook notification for "{payment_id}" with status "{status_detail}"'), target_fixture="response")
def receive_webhook(client, payment_id, status_detail):
    payload = {
        "action": "order.processed", 
        "data": {
            "id": "123456",
            "external_reference": payment_id, 
            "total_paid_amount": 10.0,
            "total_amount": 10.0,
            "status": "approved" if status_detail == "accredited" else "rejected",
            "status_detail": status_detail
        }
    }
    return client.post("/api/v1/webhook/", json=payload)

@then(parsers.parse('the payment status should be updated to "{expected_status}"'))
def check_update(mock_repository, expected_status, response):
    if response.status_code not in [200, 201, 204]:
        pytest.fail(f"API Error {response.status_code}: {response.json()}")

    mock_repository.update_status.assert_called()
    call_args = mock_repository.update_status.call_args
    assert call_args[0][1] == expected_status

@then(parsers.parse('the response status code should be {status_code:d}'))
def check_status_code(response, status_code):
    if response.status_code != status_code:
         print(f"DEBUG BODY: {response.json()}")
    assert response.status_code == status_code