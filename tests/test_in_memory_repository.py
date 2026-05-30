"""Tests for consumer.adapters.in_memory_rewards_repository.InMemoryRewardsRepository."""

import pytest

from consumer.adapters.in_memory_rewards_repository import InMemoryRewardsRepository
from consumer.domain.models import RewardsAccount


@pytest.fixture
def repository() -> InMemoryRewardsRepository:
    """Provide a fresh repository for each test."""
    return InMemoryRewardsRepository()


@pytest.fixture
def sample_account() -> RewardsAccount:
    """Provide a sample rewards account."""
    return RewardsAccount(
        numero_tarjeta="4111111111111111",
        puntos_acumulados=100,
        cashback_acumulado=2.0,
    )


class TestGetAccount:
    """Tests for InMemoryRewardsRepository.get_account."""

    def test_get_nonexistent_account_returns_none(self, repository):
        """get_account for an unknown card must return None."""
        result = repository.get_account("0000000000000000")
        assert result is None

    def test_get_account_after_save(self, repository, sample_account):
        """get_account must return the saved account."""
        repository.save_account(sample_account)
        result = repository.get_account("4111111111111111")
        assert result is not None
        assert result.numero_tarjeta == "4111111111111111"

    def test_get_account_returns_same_object(self, repository, sample_account):
        """get_account must return the exact object that was saved."""
        repository.save_account(sample_account)
        result = repository.get_account("4111111111111111")
        assert result is sample_account


class TestSaveAccount:
    """Tests for InMemoryRewardsRepository.save_account."""

    def test_save_new_account(self, repository):
        """Saving a new account must make it retrievable."""
        account = RewardsAccount(numero_tarjeta="1234567890123456")
        repository.save_account(account)
        assert repository.get_account("1234567890123456") is account

    def test_save_overwrites_existing_account(self, repository, sample_account):
        """Saving an account with the same tarjeta must overwrite the old one."""
        repository.save_account(sample_account)

        updated_account = RewardsAccount(
            numero_tarjeta="4111111111111111",
            puntos_acumulados=999,
            cashback_acumulado=9.99,
        )
        repository.save_account(updated_account)

        result = repository.get_account("4111111111111111")
        assert result.puntos_acumulados == 999
        assert result.cashback_acumulado == pytest.approx(9.99)

    def test_save_multiple_accounts(self, repository):
        """Multiple distinct accounts should coexist in the repository."""
        acc1 = RewardsAccount(numero_tarjeta="1111", puntos_acumulados=10)
        acc2 = RewardsAccount(numero_tarjeta="2222", puntos_acumulados=20)
        acc3 = RewardsAccount(numero_tarjeta="3333", puntos_acumulados=30)

        repository.save_account(acc1)
        repository.save_account(acc2)
        repository.save_account(acc3)

        assert repository.get_account("1111").puntos_acumulados == 10
        assert repository.get_account("2222").puntos_acumulados == 20
        assert repository.get_account("3333").puntos_acumulados == 30

    def test_rewards_accumulation_across_saves(self, repository):
        """Simulate accumulating rewards across multiple dinner events."""
        tarjeta = "4111111111111111"
        account = RewardsAccount(numero_tarjeta=tarjeta)

        # First dinner: 500 pts, $10.00 cashback
        account.add_rewards(500, 10.0)
        repository.save_account(account)

        # Second dinner: 300 pts, $6.00 cashback
        stored = repository.get_account(tarjeta)
        stored.add_rewards(300, 6.0)
        repository.save_account(stored)

        final = repository.get_account(tarjeta)
        assert final.puntos_acumulados == 800
        assert final.cashback_acumulado == pytest.approx(16.0)
