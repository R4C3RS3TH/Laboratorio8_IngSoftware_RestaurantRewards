"""Tests for the centralised Settings configuration module."""

import os

import pytest

from config.settings import Settings, settings


class TestSettings:
    """Unit tests for the Settings class."""

    def test_default_host_is_localhost(self, monkeypatch):
        """When RABBITMQ_HOST is not set, default to localhost."""
        monkeypatch.delenv("RABBITMQ_HOST", raising=False)
        s = Settings()
        assert s.rabbitmq_host == "localhost"

    def test_host_from_env(self, monkeypatch):
        """RABBITMQ_HOST env var is picked up correctly."""
        monkeypatch.setenv("RABBITMQ_HOST", "192.168.1.100")
        s = Settings()
        assert s.rabbitmq_host == "192.168.1.100"

    def test_default_port_is_5672(self, monkeypatch):
        """When RABBITMQ_PORT is not set, default to 5672."""
        monkeypatch.delenv("RABBITMQ_PORT", raising=False)
        s = Settings()
        assert s.rabbitmq_port == 5672

    def test_port_from_env(self, monkeypatch):
        """RABBITMQ_PORT env var is converted to int."""
        monkeypatch.setenv("RABBITMQ_PORT", "5673")
        s = Settings()
        assert s.rabbitmq_port == 5673

    def test_default_username_is_guest(self, monkeypatch):
        """When RABBITMQ_USERNAME is not set, default to guest."""
        monkeypatch.delenv("RABBITMQ_USERNAME", raising=False)
        s = Settings()
        assert s.rabbitmq_username == "guest"

    def test_username_from_env(self, monkeypatch):
        """RABBITMQ_USERNAME env var is picked up correctly."""
        monkeypatch.setenv("RABBITMQ_USERNAME", "myuser")
        s = Settings()
        assert s.rabbitmq_username == "myuser"

    def test_default_password_is_guest(self, monkeypatch):
        """When RABBITMQ_PASSWORD is not set, default to guest."""
        monkeypatch.delenv("RABBITMQ_PASSWORD", raising=False)
        s = Settings()
        assert s.rabbitmq_password == "guest"

    def test_password_from_env(self, monkeypatch):
        """RABBITMQ_PASSWORD env var is picked up correctly."""
        monkeypatch.setenv("RABBITMQ_PASSWORD", "s3cr3t")
        s = Settings()
        assert s.rabbitmq_password == "s3cr3t"

    def test_default_vhost_is_slash(self, monkeypatch):
        """When RABBITMQ_VHOST is not set, default to /."""
        monkeypatch.delenv("RABBITMQ_VHOST", raising=False)
        s = Settings()
        assert s.rabbitmq_vhost == "/"

    def test_vhost_from_env(self, monkeypatch):
        """RABBITMQ_VHOST env var is picked up correctly."""
        monkeypatch.setenv("RABBITMQ_VHOST", "/production")
        s = Settings()
        assert s.rabbitmq_vhost == "/production"

    def test_default_queue_name(self, monkeypatch):
        """When RABBITMQ_QUEUE is not set, default to rewards_queue."""
        monkeypatch.delenv("RABBITMQ_QUEUE", raising=False)
        s = Settings()
        assert s.rabbitmq_queue == "rewards_queue"

    def test_queue_from_env(self, monkeypatch):
        """RABBITMQ_QUEUE env var is picked up correctly."""
        monkeypatch.setenv("RABBITMQ_QUEUE", "laboratorio_1")
        s = Settings()
        assert s.rabbitmq_queue == "laboratorio_1"

    def test_module_singleton_is_settings_instance(self):
        """The module-level `settings` object is a Settings instance."""
        assert isinstance(settings, Settings)
