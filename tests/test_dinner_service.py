"""Tests for producer.application.dinner_service.DinnerService."""

from datetime import datetime
from unittest.mock import MagicMock, call

import pytest

from producer.application.dinner_service import DinnerService
from producer.domain.models import DinnerEvent
from producer.ports.message_publisher_port import MessagePublisherPort


@pytest.fixture
def mock_publisher() -> MagicMock:
    """Provide a mock MessagePublisherPort."""
    return MagicMock(spec=MessagePublisherPort)


@pytest.fixture
def dinner_service(mock_publisher) -> DinnerService:
    """Provide a DinnerService with a mock publisher."""
    return DinnerService(publisher=mock_publisher)


@pytest.fixture
def sample_event() -> DinnerEvent:
    """Provide a sample valid DinnerEvent."""
    return DinnerEvent(
        monto_consumido=200.0,
        numero_tarjeta="4111111111111111",
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 30, 20, 0, 0),
    )


class TestDinnerServiceRegisterDinner:
    """Tests for DinnerService.register_dinner."""

    def test_register_dinner_calls_publish_once(self, dinner_service, mock_publisher, sample_event):
        """register_dinner must call publisher.publish exactly once."""
        dinner_service.register_dinner(sample_event)
        mock_publisher.publish.assert_called_once()

    def test_register_dinner_passes_correct_event(self, dinner_service, mock_publisher, sample_event):
        """register_dinner must pass the exact event to the publisher."""
        dinner_service.register_dinner(sample_event)
        mock_publisher.publish.assert_called_once_with(sample_event)

    def test_register_dinner_does_not_swallow_publisher_errors(
        self, dinner_service, mock_publisher, sample_event
    ):
        """If the publisher raises, the exception should propagate."""
        mock_publisher.publish.side_effect = RuntimeError("Broker unavailable")
        with pytest.raises(RuntimeError, match="Broker unavailable"):
            dinner_service.register_dinner(sample_event)

    def test_register_dinner_can_handle_multiple_events(
        self, dinner_service, mock_publisher
    ):
        """register_dinner called multiple times should call publish each time."""
        event_1 = DinnerEvent(100.0, "1111", "R-1")
        event_2 = DinnerEvent(200.0, "2222", "R-2")

        dinner_service.register_dinner(event_1)
        dinner_service.register_dinner(event_2)

        assert mock_publisher.publish.call_count == 2
        mock_publisher.publish.assert_has_calls([call(event_1), call(event_2)])
