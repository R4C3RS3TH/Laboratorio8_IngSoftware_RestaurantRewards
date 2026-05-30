"""In-memory implementation of RewardsRepositoryPort.

Suitable for development, testing, and the lab environment. To use a
persistent database in the future, simply create a new adapter that
implements RewardsRepositoryPort — zero changes to the domain or
application layer required.
"""

from typing import Optional

from consumer.domain.models import RewardsAccount
from consumer.ports.rewards_repository_port import RewardsRepositoryPort


class InMemoryRewardsRepository(RewardsRepositoryPort):
    """Stores reward accounts in a plain Python dictionary."""

    def __init__(self) -> None:
        self._store: dict[str, RewardsAccount] = {}

    def get_account(self, numero_tarjeta: str) -> Optional[RewardsAccount]:
        """Return the account for the given card number, or None if not found.

        Args:
            numero_tarjeta: Customer's card number.

        Returns:
            RewardsAccount or None.
        """
        return self._store.get(numero_tarjeta)

    def save_account(self, account: RewardsAccount) -> None:
        """Persist (upsert) a rewards account.

        Args:
            account: The account to store. Overwrites any existing entry
                     for the same numero_tarjeta.
        """
        self._store[account.numero_tarjeta] = account
