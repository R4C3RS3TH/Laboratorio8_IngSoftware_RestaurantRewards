"""Port (driving-side interface) for message publishing.

Following Hexagonal Architecture, this ABC defines what the application
layer needs from any messaging infrastructure, without coupling to any
specific broker implementation.
"""

from abc import ABC, abstractmethod

from producer.domain.models import DinnerEvent


class MessagePublisherPort(ABC):
    """Abstract port for publishing dinner events to a message broker."""

    @abstractmethod
    def publish(self, event: DinnerEvent) -> None:
        """Publish a DinnerEvent to the message broker.

        Args:
            event: The dinner event to be serialized and published.
        """
