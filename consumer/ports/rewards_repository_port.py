"""Port for persisting and retrieving reward accounts.

Defines the secondary (driven) port that the application layer uses to
store and fetch RewardsAccount data. Concrete implementations can be
in-memory, relational DB, NoSQL, etc., without affecting business logic.
"""

from abc import ABC, abstractmethod
from typing import Optional

from consumer.domain.models import RewardsAccount


class RewardsRepositoryPort(ABC):
    """Abstract port for RewardsAccount persistence."""

    @abstractmethod
    def get_account(self, numero_tarjeta: str) -> Optional[RewardsAccount]:
        """Retrieve a customer's rewards account by card number.

        Args:
            numero_tarjeta: The customer's card number.

        Returns:
            The RewardsAccount if found, or None if the customer has no account.
        """

    @abstractmethod
    def save_account(self, account: RewardsAccount) -> None:
        """Persist (create or update) a customer's rewards account.

        Args:
            account: The RewardsAccount instance to persist.
        """
