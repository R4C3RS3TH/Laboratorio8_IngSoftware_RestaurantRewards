"""Entry point for the Restaurant System (Producer).

Runs an interactive CLI that collects dinner data from the user and
publishes it to the RabbitMQ broker via the Hexagonal Architecture stack.

Usage:
    python -m producer.main_producer
    # or
    python producer/main_producer.py
"""

import logging
import sys
from datetime import datetime

from producer.adapters.rabbitmq_publisher_adapter import RabbitMQPublisherAdapter
from producer.application.dinner_service import DinnerService
from producer.domain.models import DinnerEvent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def _prompt_dinner_event() -> DinnerEvent:
    """Interactively prompt the user for dinner event data.

    Returns:
        A validated DinnerEvent instance.

    Raises:
        ValueError: If the user provides invalid input.
    """
    print("\n" + "=" * 55)
    print("  🍽️  SISTEMA DEL RESTAURANTE — Registrar Cena")
    print("=" * 55)

    numero_tarjeta = input("  Número de tarjeta del cliente : ").strip()
    codigo_restaurante = input("  Código del restaurante        : ").strip()
    monto_str = input("  Monto consumido               : ").strip()
    monto_consumido = float(monto_str)

    return DinnerEvent(
        monto_consumido=monto_consumido,
        numero_tarjeta=numero_tarjeta,
        codigo_restaurante=codigo_restaurante,
        fecha_hora=datetime.now(),
    )


def main() -> None:
    """Main entry point: wires up dependencies and runs the producer loop."""
    publisher = RabbitMQPublisherAdapter()
    service = DinnerService(publisher)

    print("\n  Bienvenido al Sistema del Restaurante.")
    print("  (Ingresa 'salir' en cualquier campo para terminar)\n")

    while True:
        try:
            event = _prompt_dinner_event()
            service.register_dinner(event)
            print(f"\n  ✅ Evento publicado para tarjeta {event.numero_tarjeta}.\n")
        except ValueError as exc:
            print(f"\n  ⚠️  Dato inválido: {exc}. Intenta de nuevo.\n")
        except KeyboardInterrupt:
            print("\n\n  Saliendo del sistema del restaurante. ¡Hasta luego!\n")
            sys.exit(0)
        except Exception as exc:  # noqa: BLE001
            logger.error("Error inesperado al publicar evento: %s", exc)
            print(f"\n  ❌ Error de conexión con el broker: {exc}\n")

        continuar = input("  ¿Registrar otra cena? (s/n): ").strip().lower()
        if continuar != "s":
            print("\n  ¡Hasta luego!\n")
            break


if __name__ == "__main__":
    main()
