
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.monitoring import HealthMonitor

@patch('src.monitoring.requests.get')
def test_check_health_success(mock_get):
    """Test du ping réussi."""
    # Simulation d'une réponse 200 OK
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    monitor = HealthMonitor("http://fake-url.com")
    success, msg = monitor.check_health()
    
    assert success is True
    assert "Status Code: 200" in msg

@patch('src.monitoring.requests.get')
def test_check_health_failure(mock_get):
    """Test du ping échoué (404/500)."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    monitor = HealthMonitor("http://fake-url.com")
    success, msg = monitor.check_health()
    
    assert success is False
    assert "Error Code: 500" in msg
