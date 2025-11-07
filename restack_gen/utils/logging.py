"""Structured logging utilities for the Restack Gen CLI."""

from __future__ import annotations

import json
import logging
from logging import Logger
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

from ..models.config import LoggingConfig


def configure_logging(config: LoggingConfig) -> Logger:
    """Configure application logging based on the provided config."""
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger = logging.getLogger("restack_gen")
    logger.setLevel(level)
    logger.handlers.clear()

    handler: logging.Handler
    if config.format == "json":
        handler = JSONLogHandler(config)
    else:
        handler = RichHandler(console=Console(), rich_tracebacks=True, markup=True)
    handler.setLevel(level)
    logger.addHandler(handler)
    return logger


class JSONLogHandler(logging.Handler):
    """Simple JSON logging handler for structured output."""

    def __init__(self, config: LoggingConfig) -> None:
        super().__init__()
        self.config = config
        # Use a standard formatter to leverage time/exception formatting helpers
        self._formatter = logging.Formatter()

    def emit(self, record: logging.LogRecord) -> None:
        log_entry: dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if self.config.include_timestamp:
            log_entry["timestamp"] = self._formatter.formatTime(record)
        if self.config.include_caller and record.pathname:
            log_entry["caller"] = f"{record.pathname}:{record.lineno}"
        if record.exc_info:
            log_entry["exception"] = self._formatter.formatException(record.exc_info)
        output = json.dumps(log_entry)

        if self.config.output_file:
            with open(self.config.output_file, "a", encoding="utf-8") as file:
                file.write(output + "\n")
        else:
            print(output)


def get_logger(name: str | None = None) -> Logger:
    """Get a child logger with a specific name."""
    return logging.getLogger("restack_gen" if name is None else f"restack_gen.{name}")
