"""Tests for consumer.domain.rewards_calculator.RewardsCalculator."""

import pytest

from consumer.domain.rewards_calculator import RewardsCalculator


@pytest.fixture
def calculator() -> RewardsCalculator:
    """Provide a fresh RewardsCalculator instance for each test."""
    return RewardsCalculator()


class TestCalculatePoints:
    """Tests for RewardsCalculator.calculate_points."""

    def test_points_for_standard_amount(self, calculator):
        """100 units should yield 1000 points (10 pts/unit)."""
        assert calculator.calculate_points(100.0) == 1000

    def test_points_for_fractional_amount(self, calculator):
        """Fractional amounts should be truncated (int conversion)."""
        # 15.75 * 10 = 157.5 → int → 157
        assert calculator.calculate_points(15.75) == 157

    def test_points_for_minimum_amount(self, calculator):
        """Even a small amount above 0 should yield at least 1 point range."""
        assert calculator.calculate_points(0.1) == 1

    def test_points_for_large_amount(self, calculator):
        """Large amounts should scale linearly."""
        assert calculator.calculate_points(1000.0) == 10000

    def test_zero_monto_returns_zero_points(self, calculator):
        """Zero monto should yield 0 points."""
        assert calculator.calculate_points(0) == 0

    def test_negative_monto_returns_zero_points(self, calculator):
        """Negative monto should yield 0 points, not raise an error."""
        assert calculator.calculate_points(-50.0) == 0

    def test_points_rate_constant(self, calculator):
        """The POINTS_PER_UNIT constant should be 10."""
        assert RewardsCalculator.POINTS_PER_UNIT == 10


class TestCalculateCashback:
    """Tests for RewardsCalculator.calculate_cashback."""

    def test_cashback_for_standard_amount(self, calculator):
        """100 units should yield 2.00 cashback (2%)."""
        assert calculator.calculate_cashback(100.0) == pytest.approx(2.0)

    def test_cashback_for_fractional_amount(self, calculator):
        """Cashback should be rounded to 2 decimal places."""
        # 33.33 * 0.02 = 0.6666 → rounded → 0.67
        assert calculator.calculate_cashback(33.33) == pytest.approx(0.67)

    def test_cashback_for_large_amount(self, calculator):
        """Large amounts should scale linearly."""
        assert calculator.calculate_cashback(500.0) == pytest.approx(10.0)

    def test_zero_monto_returns_zero_cashback(self, calculator):
        """Zero monto should yield 0.0 cashback."""
        assert calculator.calculate_cashback(0) == 0.0

    def test_negative_monto_returns_zero_cashback(self, calculator):
        """Negative monto should yield 0.0 cashback."""
        assert calculator.calculate_cashback(-20.0) == 0.0

    def test_cashback_rate_constant(self, calculator):
        """The CASHBACK_RATE constant should be 0.02 (2%)."""
        assert RewardsCalculator.CASHBACK_RATE == pytest.approx(0.02)
