"""Application service for the Producer (Restaurant System).

This is the Use Case layer. It orchestrates domain objects and communicates
with the outside world exclusively via Ports — never via concrete adapters.
This makes the service 100% testable without a real message broker.
"""

import logging

from producer.domain.models import DinnerEvent
from producer.ports.message_publisher_port import MessagePublisherPort

logger = logging.getLogger(__name__)


class DinnerService:
    """Orchestrates the registration and publication of a dinner event.

    Depends only on the MessagePublisherPort abstraction, not on any
    concrete infrastructure (RabbitMQ, Kafka, etc.).
    """

    def __init__(self, publisher: MessagePublisherPort) -> None:
        """Initialize with an injected publisher port.

        Args:
            publisher: Any implementation of MessagePublisherPort.
        """
        self._publisher = publisher

    def register_dinner(self, event: DinnerEvent) -> None:
        """Register a dinner consumption event and publish it to the broker.

        Args:
            event: A validated DinnerEvent domain object.
        """
        logger.info(
            "Registrando cena — tarjeta: %s | restaurante: %s | monto: %.2f",
            event.numero_tarjeta,
            event.codigo_restaurante,
            event.monto_consumido,
        )
        self._publisher.publish(event)
        logger.info("Cena publicada exitosamente al broker de mensajería.")
