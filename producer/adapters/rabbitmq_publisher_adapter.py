"""RabbitMQ adapter implementing MessagePublisherPort.

This is the ONLY file in the producer that imports pika. The rest of the
system is completely unaware of RabbitMQ.

All connection parameters are read from environment variables via
``config.settings`` — no secrets are hardcoded here.
See ``.env.example`` for the full list of supported variables.
"""

import logging

import pika
import pika.exceptions

from config.settings import settings
from producer.domain.models import DinnerEvent
from producer.ports.message_publisher_port import MessagePublisherPort

logger = logging.getLogger(__name__)


class RabbitMQPublisherAdapter(MessagePublisherPort):
    """Publishes DinnerEvent messages to a RabbitMQ queue using pika."""

    def __init__(self) -> None:
        self._queue_name: str = settings.rabbitmq_queue
        self._connection_params = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            virtual_host=settings.rabbitmq_vhost,
            credentials=pika.PlainCredentials(
                settings.rabbitmq_username,
                settings.rabbitmq_password,
            ),
            heartbeat=60,
            blocked_connection_timeout=300,
        )

    def publish(self, event: DinnerEvent) -> None:
        """Serialize and publish a DinnerEvent to the RabbitMQ queue.

        Opens a connection, publishes the message with delivery_mode=2
        (persistent), then closes the connection cleanly.

        Args:
            event: The dinner event to publish.

        Raises:
            pika.exceptions.AMQPConnectionError: If the broker is unreachable.
        """
        connection = pika.BlockingConnection(self._connection_params)
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self._queue_name, durable=True)
            message_body = event.to_json()
            channel.basic_publish(
                exchange="",
                routing_key=self._queue_name,
                body=message_body.encode("utf-8"),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,
                    content_type="application/json",
                ),
            )
            logger.info(
                "Evento publicado en '%s': tarjeta=%s restaurante=%s monto=%.2f",
                self._queue_name,
                event.numero_tarjeta,
                event.codigo_restaurante,
                event.monto_consumido,
            )
        finally:
            connection.close()
