"""Application service for the Consumer (Rewards System).

Orchestrates the full use case:
  1. Deserialize the raw JSON message from the broker.
  2. Calculate points and cashback using the domain calculator.
  3. Update (or create) the customer's rewards account via the repository.
  4. Log the result.

This service depends exclusively on Ports — never on pika, databases, or
any other infrastructure. It is fully testable with mocks.

Extensibility note:
  To send notifications (SMS, Email) after processing, inject a
  NotificationPort here and call it after step 3, without touching
  any other class.
"""

import logging

from consumer.domain.models import DinnerEventMessage, RewardsAccount
from consumer.domain.rewards_calculator import RewardsCalculator
from consumer.ports.rewards_repository_port import RewardsRepositoryPort

logger = logging.getLogger(__name__)


class RewardsService:
    """Processes incoming dinner events and updates reward accounts."""

    def __init__(
        self,
        calculator: RewardsCalculator,
        repository: RewardsRepositoryPort,
    ) -> None:
        """Initialize the service with injected dependencies.

        Args:
            calculator: Domain calculator for points and cashback.
            repository: Port for persisting reward accounts.
        """
        self._calculator = calculator
        self._repository = repository

    def process_dinner_event(self, raw_message: bytes) -> None:
        """Process a raw broker message and update the customer's rewards.

        If the message is malformed or missing fields, the error is logged
        and the exception is re-raised so the adapter can nack the message.

        Args:
            raw_message: Raw bytes from the message broker (expected JSON).

        Raises:
            KeyError:     If a required JSON field is missing.
            ValueError:   If a field has an invalid value or JSON is malformed.
            json.JSONDecodeError: If the payload is not valid JSON.
        """
        event = DinnerEventMessage.from_json(raw_message)

        puntos = self._calculator.calculate_points(event.monto_consumido)
        cashback = self._calculator.calculate_cashback(event.monto_consumido)

        account = self._repository.get_account(event.numero_tarjeta)
        if account is None:
            account = RewardsAccount(numero_tarjeta=event.numero_tarjeta)

        account.add_rewards(puntos, cashback)
        self._repository.save_account(account)

        logger.info(
            "✅ Recompensas actualizadas | tarjeta: %s | restaurante: %s | "
            "monto: %.2f | puntos ganados: %d | cashback ganado: %.2f | "
            "total puntos: %d | total cashback: %.2f",
            event.numero_tarjeta,
            event.codigo_restaurante,
            event.monto_consumido,
            puntos,
            cashback,
            account.puntos_acumulados,
            account.cashback_acumulado,
        )
