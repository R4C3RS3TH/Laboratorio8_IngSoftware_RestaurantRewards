"""Centralised configuration for the Restaurant Rewards system.

All broker connection parameters are read from environment variables so
that no secrets or environment-specific values are ever hardcoded.

Usage::

    from config.settings import settings

    print(settings.rabbitmq_host)

Environment variables (see .env.example):

    RABBITMQ_HOST      – RabbitMQ broker hostname or IP   (default: localhost)
    RABBITMQ_PORT      – AMQP port                        (default: 5672)
    RABBITMQ_USERNAME  – Broker username                  (default: guest)
    RABBITMQ_PASSWORD  – Broker password                  (default: guest)
    RABBITMQ_VHOST     – Virtual host                     (default: /)
    RABBITMQ_QUEUE     – Queue / routing key name         (default: rewards_queue)
"""

import os
from pathlib import Path

# Load environment variables from .env file directly (no third-party packages required)
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    with open(_env_path, "r", encoding="utf-8") as f:
        for _line in f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())


class Settings:
    """Immutable bag of configuration values loaded from environment variables."""

    @property
    def rabbitmq_host(self) -> str:
        """RabbitMQ broker hostname or IP address."""
        return os.environ.get("RABBITMQ_HOST", "localhost")

    @property
    def rabbitmq_port(self) -> int:
        """AMQP port (integer)."""
        return int(os.environ.get("RABBITMQ_PORT", "5672"))

    @property
    def rabbitmq_username(self) -> str:
        """Broker username."""
        return os.environ.get("RABBITMQ_USERNAME", "guest")

    @property
    def rabbitmq_password(self) -> str:
        """Broker password."""
        return os.environ.get("RABBITMQ_PASSWORD", "guest")

    @property
    def rabbitmq_vhost(self) -> str:
        """RabbitMQ virtual host."""
        return os.environ.get("RABBITMQ_VHOST", "/")

    @property
    def rabbitmq_queue(self) -> str:
        """Queue (or routing-key) name shared by producer and consumer."""
        return os.environ.get("RABBITMQ_QUEUE", "rewards_queue")


# Module-level singleton — import and use directly.
settings = Settings()
