from __future__ import annotations

import logging

from app.config import LOG_LEVEL


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        return

    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format=LOG_FORMAT)


logger = logging.getLogger("document_processing_pipeline")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
