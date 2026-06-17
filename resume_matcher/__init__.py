from __future__ import annotations

import logging

from .config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format=settings.log_format,
    force=True,
)

logger = logging.getLogger(__name__)
logger.debug("Logging configured at %s level", settings.log_level)
