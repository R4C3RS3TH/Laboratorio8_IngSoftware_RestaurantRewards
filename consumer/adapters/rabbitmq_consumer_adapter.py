"""RabbitMQ adapter implementing MessageConsumerPort.

This is the ONLY file in the consumer that imports pika. It handles:
  - Connection and channel setup.
  - Queue declaration (durable=True, matching the producer).
  - Manual acknowledgment (auto_ack=False) for reliability: if the
    callback raises an exception, the message is nack'd and requeued.

All connection parameters are read from environment variables via
``config.settings`` — no secrets are hardcoded here.
See ``.env.example`` for the full list of supported variables.
"""

import logging
from typing import Callable

import pika
import pika.exceptions

from config.settings import settings
from consumer.ports.message_consumer_port import MessageConsumerPort

logger = logging.getLogger(__name__)


class RabbitMQConsumerAdapter(MessageConsumerPort):
    """Consumes messages from a RabbitMQ queue and dispatches them to a callback."""

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

    def start_consuming(self, callback: Callable[[bytes], None]) -> None:
        """Connect to RabbitMQ and block until interrupted, calling callback
        for each received message.

        Uses manual acknowledgment: the message is ack'd after the callback
        returns successfully, or nack'd (requeued) if it raises an exception.

        Args:
            callback: Function to call with the raw message bytes.
        """
        connection = pika.BlockingConnection(self._connection_params)
        channel = connection.channel()
        channel.queue_declare(queue=self._queue_name, durable=True)

        # Limit to 1 unacknowledged message at a time for fairness
        channel.basic_qos(prefetch_count=1)

        def _on_message(ch, method, _properties, body: bytes) -> None:
            try:
                callback(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.debug("Mensaje procesado y confirmado (ack).")
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Error al procesar mensaje. El mensaje será reencolado (nack)."
                )
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=_on_message,
            auto_ack=False,
        )

        logger.info(
            "🎧 Consumidor iniciado. Esperando mensajes en '%s'. "
            "Presiona Ctrl+C para salir.",
            self._queue_name,
        )
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Consumidor detenido por el usuario.")
            channel.stop_consuming()
        finally:
            connection.close()
