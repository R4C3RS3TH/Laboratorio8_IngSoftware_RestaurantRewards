"""Tests for consumer.application.rewards_service.RewardsService."""

import json
from datetime import datetime
from unittest.mock import MagicMock, call

import pytest

from consumer.application.rewards_service import RewardsService
from consumer.domain.models import RewardsAccount
from consumer.domain.rewards_calculator import RewardsCalculator
from consumer.ports.rewards_repository_port import RewardsRepositoryPort


def _make_raw_message(
    monto: float = 100.0,
    tarjeta: str = "4111111111111111",
    restaurante: str = "REST-001",
    fecha_hora: str = "2026-05-30T20:00:00",
) -> bytes:
    """Helper: build a raw JSON message as bytes."""
    return json.dumps(
        {
            "monto_consumido": monto,
            "numero_tarjeta": tarjeta,
            "codigo_restaurante": restaurante,
            "fecha_hora": fecha_hora,
        }
    ).encode("utf-8")


@pytest.fixture
def mock_repository() -> MagicMock:
    """Provide a mock RewardsRepositoryPort."""
    return MagicMock(spec=RewardsRepositoryPort)


@pytest.fixture
def real_calculator() -> RewardsCalculator:
    """Provide a real RewardsCalculator (it's stateless, no need to mock)."""
    return RewardsCalculator()


@pytest.fixture
def rewards_service(real_calculator, mock_repository) -> RewardsService:
    """Provide a RewardsService with a real calculator and mock repository."""
    return RewardsService(calculator=real_calculator, repository=mock_repository)


class TestRewardsServiceNewCustomer:
    """Tests for a customer with no existing account."""

    def test_creates_new_account_when_none_exists(self, rewards_service, mock_repository):
        """When get_account returns None, a new account must be saved."""
        mock_repository.get_account.return_value = None
        rewards_service.process_dinner_event(_make_raw_message(monto=100.0, tarjeta="1111"))

        mock_repository.save_account.assert_called_once()
        saved_account: RewardsAccount = mock_repository.save_account.call_args[0][0]
        assert saved_account.numero_tarjeta == "1111"
        assert saved_account.puntos_acumulados == 1000   # 100 * 10
        assert saved_account.cashback_acumulado == pytest.approx(2.0)  # 100 * 2%

    def test_get_account_called_with_correct_card(self, rewards_service, mock_repository):
        """get_account must be called with the tarjeta from the message."""
        mock_repository.get_account.return_value = None
        rewards_service.process_dinner_event(_make_raw_message(tarjeta="9999"))
        mock_repository.get_account.assert_called_once_with("9999")


class TestRewardsServiceExistingCustomer:
    """Tests for a customer with an existing account."""

    def test_accumulates_rewards_on_existing_account(self, rewards_service, mock_repository):
        """Rewards must be added to the existing account, not replace it."""
        existing_account = RewardsAccount(
            numero_tarjeta="4111111111111111",
            puntos_acumulados=500,
            cashback_acumulado=1.0,
        )
        mock_repository.get_account.return_value = existing_account

        rewards_service.process_dinner_event(_make_raw_message(monto=100.0, tarjeta="4111111111111111"))

        saved_account: RewardsAccount = mock_repository.save_account.call_args[0][0]
        assert saved_account.puntos_acumulados == 1500   # 500 + 1000
        assert saved_account.cashback_acumulado == pytest.approx(3.0)  # 1.0 + 2.0

    def test_save_account_called_once(self, rewards_service, mock_repository):
        """save_account must be called exactly once per processed message."""
        mock_repository.get_account.return_value = None
        rewards_service.process_dinner_event(_make_raw_message())
        mock_repository.save_account.assert_called_once()


class TestRewardsServiceMalformedMessages:
    """Tests for error handling with bad input."""

    def test_missing_field_raises_key_error(self, rewards_service, mock_repository):
        """A JSON message missing a required field must raise KeyError."""
        incomplete = json.dumps(
            {"monto_consumido": 100.0, "numero_tarjeta": "1234"}
        ).encode()
        with pytest.raises(KeyError):
            rewards_service.process_dinner_event(incomplete)

    def test_invalid_json_raises_value_error(self, rewards_service, mock_repository):
        """Non-JSON bytes must raise a json decode error."""
        import json as _json
        with pytest.raises(_json.JSONDecodeError):
            rewards_service.process_dinner_event(b"not-valid-json")

    def test_invalid_monto_type_raises_value_error(self, rewards_service, mock_repository):
        """A non-numeric monto_consumido must raise ValueError."""
        bad_message = json.dumps(
            {
                "monto_consumido": "not-a-number",
                "numero_tarjeta": "1234",
                "codigo_restaurante": "R-1",
                "fecha_hora": "2026-01-01T00:00:00",
            }
        ).encode()
        with pytest.raises(ValueError):
            rewards_service.process_dinner_event(bad_message)

    def test_negative_monto_raises_value_error(self, rewards_service, mock_repository):
        """A message with a negative or zero monto must be rejected immediately."""
        bad_message = _make_raw_message(monto=-50.0)
        with pytest.raises(ValueError, match="monto_consumido"):
            rewards_service.process_dinner_event(bad_message)

    def test_empty_card_raises_value_error(self, rewards_service, mock_repository):
        """A message with an empty card number must be rejected."""
        bad_message = _make_raw_message(tarjeta="   ")
        with pytest.raises(ValueError, match="numero_tarjeta"):
            rewards_service.process_dinner_event(bad_message)

    def test_empty_restaurant_raises_value_error(self, rewards_service, mock_repository):
        """A message with an empty restaurant code must be rejected."""
        bad_message = _make_raw_message(restaurante="")
        with pytest.raises(ValueError, match="codigo_restaurante"):
            rewards_service.process_dinner_event(bad_message)

    def test_repository_not_called_on_bad_message(self, rewards_service, mock_repository):
        """If deserialization fails, the repository must NOT be called."""
        mock_repository.get_account.return_value = None
        with pytest.raises(Exception):  # noqa: B017
            rewards_service.process_dinner_event(b"bad json")
        mock_repository.save_account.assert_not_called()
