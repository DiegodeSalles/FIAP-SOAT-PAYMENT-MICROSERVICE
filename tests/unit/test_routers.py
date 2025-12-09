import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.infrastructure.api import routers
from src.use_cases.get_payment_status_use_case import GetPaymentStatusUseCase
from src.use_cases.process_payment_webhook_use_case import ProcessPaymentWebhookUseCase

@patch('src.infrastructure.api.routers.settings')
def test_missing_dependencies_factories(mock_settings):
    mock_repo = MagicMock()

    status_uc = routers.get_status_use_case(mock_repo)
    assert isinstance(status_uc, GetPaymentStatusUseCase)
    
    webhook_uc = routers.get_webhook_use_case(mock_repo)
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