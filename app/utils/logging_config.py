"""Logging setup for local and cloud execution."""

from __future__ import annotations

import logging


def configure_logging() -> None:
    """Configure a concise process-wide logger."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

