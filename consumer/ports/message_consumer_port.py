"""Port for consuming messages from a message broker.

Defines the inbound interface the Consumer application layer depends on.
Any concrete messaging technology (RabbitMQ, Kafka, SQS, etc.) must
implement this ABC to be usable by the application.
"""

from abc import ABC, abstractmethod
from typing import Callable


class MessageConsumerPort(ABC):
    """Abstract port for consuming messages from a broker queue."""

    @abstractmethod
    def start_consuming(self, callback: Callable[[bytes], None]) -> None:
        """Start the message consumption loop.

        Args:
            callback: A function that receives the raw message bytes and
                      processes them. The port implementation is responsible
                      for acknowledgment after invoking the callback.
        """
