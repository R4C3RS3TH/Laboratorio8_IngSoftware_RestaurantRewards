"""Domain model for the Producer (Restaurant System).

This module contains the core DinnerEvent entity. It has zero dependencies
on external libraries (no pika, no frameworks), keeping the domain pure.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DinnerEvent:
    """Represents a dinner consumption event registered by the restaurant.

    Attributes:
        monto_consumido:     Total amount consumed (must be greater than 0).
        numero_tarjeta:      Customer card number (non-empty string).
        codigo_restaurante:  Unique restaurant identifier (non-empty string).
        fecha_hora:          Date and time when the dinner took place.
    """

    monto_consumido: float
    numero_tarjeta: str
    codigo_restaurante: str
    fecha_hora: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate domain invariants after initialization."""
        if self.monto_consumido <= 0:
            raise ValueError(
                f"monto_consumido debe ser mayor que 0, se recibió: {self.monto_consumido}"
            )
        if not self.numero_tarjeta or not self.numero_tarjeta.strip():
            raise ValueError("numero_tarjeta no puede estar vacío.")
        if not self.codigo_restaurante or not self.codigo_restaurante.strip():
            raise ValueError("codigo_restaurante no puede estar vacío.")

    def to_json(self) -> str:
        """Serialize the event to a JSON string for publishing to the broker.

        Returns:
            A JSON string with the four required fields:
            monto_consumido, numero_tarjeta, codigo_restaurante, fecha_hora.
        """
        payload = {
            "monto_consumido": self.monto_consumido,
            "numero_tarjeta": self.numero_tarjeta,
            "codigo_restaurante": self.codigo_restaurante,
            "fecha_hora": self.fecha_hora.isoformat(),
        }
        return json.dumps(payload, ensure_ascii=False)
