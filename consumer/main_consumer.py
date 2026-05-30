"""Entry point for the Rewards System (Consumer).

Wires up the Hexagonal Architecture stack and starts the blocking message
consumption loop. Runs until interrupted with Ctrl+C.

Usage:
    python -m consumer.main_consumer
    # or
    python consumer/main_consumer.py
"""

import logging

from consumer.adapters.in_memory_rewards_repository import InMemoryRewardsRepository
from consumer.adapters.rabbitmq_consumer_adapter import RabbitMQConsumerAdapter
from consumer.application.rewards_service import RewardsService
from consumer.domain.rewards_calculator import RewardsCalculator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point: assembles the dependency graph and starts consuming."""
    # --- Dependency Injection (Composition Root) ---
    calculator = RewardsCalculator()
    repository = InMemoryRewardsRepository()
    rewards_service = RewardsService(calculator=calculator, repository=repository)
    consumer_adapter = RabbitMQConsumerAdapter()
    # ------------------------------------------------

    logger.info("🚀 Sistema de Recompensas iniciado.")
    logger.info(
        "Reglas activas: %d pts/$1 | %.0f%% cashback",
        RewardsCalculator.POINTS_PER_UNIT,
        RewardsCalculator.CASHBACK_RATE * 100,
    )

    consumer_adapter.start_consuming(
        callback=rewards_service.process_dinner_event,
    )

    logger.info("Sistema de Recompensas detenido.")


if __name__ == "__main__":
    main()
