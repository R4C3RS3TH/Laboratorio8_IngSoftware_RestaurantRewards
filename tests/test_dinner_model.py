"""Tests for producer.domain.models.DinnerEvent."""

import json
from datetime import datetime

import pytest

from producer.domain.models import DinnerEvent


class TestDinnerEventCreation:
    """Tests for valid DinnerEvent creation."""

    def test_create_event_with_valid_data(self):
        """A DinnerEvent should be created successfully with valid fields."""
        event = DinnerEvent(
            monto_consumido=150.75,
            numero_tarjeta="4111111111111111",
            codigo_restaurante="REST-001",
        )
        assert event.monto_consumido == 150.75
        assert event.numero_tarjeta == "4111111111111111"
        assert event.codigo_restaurante == "REST-001"
        assert isinstance(event.fecha_hora, datetime)

    def test_create_event_with_explicit_fecha_hora(self):
        """DinnerEvent should accept an explicit fecha_hora."""
        fixed_time = datetime(2026, 1, 15, 20, 30, 0)
        event = DinnerEvent(
            monto_consumido=50.0,
            numero_tarjeta="4111111111111111",
            codigo_restaurante="REST-002",
            fecha_hora=fixed_time,
        )
        assert event.fecha_hora == fixed_time

    def test_monto_as_integer_is_accepted(self):
        """An integer monto_consumido should be accepted (coerced to float logic)."""
        event = DinnerEvent(
            monto_consumido=200,
            numero_tarjeta="4111111111111111",
            codigo_restaurante="REST-001",
        )
        assert event.monto_consumido == 200


class TestDinnerEventValidation:
    """Tests for DinnerEvent domain invariants."""

    def test_zero_monto_raises_value_error(self):
        """monto_consumido of 0 must raise ValueError."""
        with pytest.raises(ValueError, match="monto_consumido"):
            DinnerEvent(
                monto_consumido=0,
                numero_tarjeta="4111111111111111",
                codigo_restaurante="REST-001",
            )

    def test_negative_monto_raises_value_error(self):
        """Negative monto_consumido must raise ValueError."""
        with pytest.raises(ValueError, match="monto_consumido"):
            DinnerEvent(
                monto_consumido=-10.0,
                numero_tarjeta="4111111111111111",
                codigo_restaurante="REST-001",
            )

    def test_empty_numero_tarjeta_raises_value_error(self):
        """An empty numero_tarjeta must raise ValueError."""
        with pytest.raises(ValueError, match="numero_tarjeta"):
            DinnerEvent(
                monto_consumido=100.0,
                numero_tarjeta="",
                codigo_restaurante="REST-001",
            )

    def test_whitespace_numero_tarjeta_raises_value_error(self):
        """A whitespace-only numero_tarjeta must raise ValueError."""
        with pytest.raises(ValueError, match="numero_tarjeta"):
            DinnerEvent(
                monto_consumido=100.0,
                numero_tarjeta="   ",
                codigo_restaurante="REST-001",
            )

    def test_empty_codigo_restaurante_raises_value_error(self):
        """An empty codigo_restaurante must raise ValueError."""
        with pytest.raises(ValueError, match="codigo_restaurante"):
            DinnerEvent(
                monto_consumido=100.0,
                numero_tarjeta="4111111111111111",
                codigo_restaurante="",
            )


class TestDinnerEventToJson:
    """Tests for DinnerEvent JSON serialization."""

    def test_to_json_returns_string(self):
        """to_json() must return a string."""
        event = DinnerEvent(
            monto_consumido=100.0,
            numero_tarjeta="4111111111111111",
            codigo_restaurante="REST-001",
        )
        assert isinstance(event.to_json(), str)

    def test_to_json_contains_required_fields(self):
        """Serialized JSON must contain all four required fields."""
        fixed_time = datetime(2026, 3, 10, 19, 0, 0)
        event = DinnerEvent(
            monto_consumido=99.99,
            numero_tarjeta="4111111111111111",
            codigo_restaurante="REST-003",
            fecha_hora=fixed_time,
        )
        payload = json.loads(event.to_json())

        assert payload["monto_consumido"] == 99.99
        assert payload["numero_tarjeta"] == "4111111111111111"
        assert payload["codigo_restaurante"] == "REST-003"
        assert payload["fecha_hora"] == fixed_time.isoformat()

    def test_to_json_no_extra_fields(self):
        """Serialized JSON must contain exactly the four required fields."""
        event = DinnerEvent(
            monto_consumido=50.0,
            numero_tarjeta="1234",
            codigo_restaurante="R-X",
        )
        payload = json.loads(event.to_json())
        expected_keys = {"monto_consumido", "numero_tarjeta", "codigo_restaurante", "fecha_hora"}
        assert set(payload.keys()) == expected_keys
