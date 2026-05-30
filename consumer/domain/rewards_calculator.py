"""Pure domain logic for calculating rewards.

This class contains ONLY business rules — no I/O, no framework dependencies.
It is deliberately stateless so it is trivially testable in isolation.

Business Rules (can be adjusted without changing any other layer):
    - Points:   10 points per unit of currency consumed.
    - Cashback: 2% of the total amount consumed.
"""


class RewardsCalculator:
    """Stateless calculator for reward points and cashback."""

    POINTS_PER_UNIT: int = 10
    CASHBACK_RATE: float = 0.02

    def calculate_points(self, monto: float) -> int:
        """Calculate reward points for a given consumption amount.

        Args:
            monto: Amount consumed (must be >= 0).

        Returns:
            Integer number of points earned. Returns 0 for non-positive amounts.
        """
        if monto <= 0:
            return 0
        return int(monto * self.POINTS_PER_UNIT)

    def calculate_cashback(self, monto: float) -> float:
        """Calculate cashback for a given consumption amount.

        Args:
            monto: Amount consumed (must be >= 0).

        Returns:
            Cashback amount rounded to 2 decimal places.
            Returns 0.0 for non-positive amounts.
        """
        if monto <= 0:
            return 0.0
        return round(monto * self.CASHBACK_RATE, 2)
