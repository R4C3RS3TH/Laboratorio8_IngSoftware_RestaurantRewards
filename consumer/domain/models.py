"""Domain models for the Consumer (Rewards System).

This module defines the data structures used when processing incoming
dinner events and managing customer reward accounts. Zero external
dependencies, keeping the domain pure and easily testable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DinnerEventMessage:
    """Represents a parsed dinner event received from the message broker.

    Attributes:
        monto_consumido:     Amount consumed during the dinner.
        numero_tarjeta:      Customer card number.
        codigo_restaurante:  Restaurant identifier.
        fecha_hora:          Date and time of the dinner.
    """

    monto_consumido: float
    numero_tarjeta: str
    codigo_restaurante: str
    fecha_hora: datetime

    def __post_init__(self) -> None:
        """Validate payload data to enforce the fail-fast principle on the consumer."""
        if self.monto_consumido <= 0:
            raise ValueError(f"El monto_consumido en el mensaje debe ser > 0, se recibió: {self.monto_consumido}")
        if not self.numero_tarjeta or not self.numero_tarjeta.strip():
            raise ValueError("El numero_tarjeta en el mensaje no puede estar vacío.")
        if not self.codigo_restaurante or not self.codigo_restaurante.strip():
            raise ValueError("El codigo_restaurante en el mensaje no puede estar vacío.")

    @classmethod
    def from_json(cls, raw: bytes | str) -> DinnerEventMessage:
        """Deserialize a JSON payload from the broker into a DinnerEventMessage.

        Args:
            raw: Raw bytes or string from the message broker.

        Returns:
            A DinnerEventMessage instance.

        Raises:
            KeyError:   If a required field is missing from the payload.
            ValueError: If the JSON is malformed or fecha_hora cannot be parsed.
        """
        data: dict = json.loads(raw)
        return cls(
            monto_consumido=float(data["monto_consumido"]),
            numero_tarjeta=str(data["numero_tarjeta"]),
            codigo_restaurante=str(data["codigo_restaurante"]),
            fecha_hora=datetime.fromisoformat(str(data["fecha_hora"])),
        )


@dataclass
class RewardsAccount:
    """Represents a customer's accumulated rewards account.

    Attributes:
        numero_tarjeta:      Customer card number (primary key).
        puntos_acumulados:   Total reward points earned.
        cashback_acumulado:  Total cashback (monetary) earned.
    """

    numero_tarjeta: str
    puntos_acumulados: int = field(default=0)
    cashback_acumulado: float = field(default=0.0)

    def add_rewards(self, puntos: int, cashback: float) -> None:
        """Accumulate new rewards into the account.

        Args:
            puntos:   Points to add.
            cashback: Cashback amount to add.
        """
        self.puntos_acumulados += puntos
        self.cashback_acumulado += round(cashback, 2)
