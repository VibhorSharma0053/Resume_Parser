# app/core/logging_config.py

import logging
import sys
from datetime import datetime


def setup_logging() -> logging.Logger:
    """
    Sets up logging for the entire application.

    Creates a logger that:
    - Prints to the terminal (console)
    - Shows timestamp, level, and message
    - Uses different colors for different levels

    Returns:
        A configured logger object
    """

    # ── Create the main logger ─────────────────────────────────
    # __name__ would give us 'app.core.logging_config'
    # We use 'resume_parser' as the app-wide logger name
    logger = logging.getLogger("resume_parser")

    # Set the minimum level we want to see
    # DEBUG = show everything
    # INFO = show info, warnings, errors
    logger.setLevel(logging.DEBUG)

    # ── Prevent adding duplicate handlers ─────────────────────
    # If setup_logging() is called multiple times,
    # we don't want duplicate log entries
    if logger.handlers:
        return logger

    # ── Create a console handler ───────────────────────────────
    # This handler sends log messages to the terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # ── Create a formatter ─────────────────────────────────────
    # This defines how each log line looks
    # Example output:
    # [2024-01-15 10:23:45] INFO     | Text extracted: 412 words
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Attach formatter to handler
    console_handler.setFormatter(formatter)

    # Attach handler to logger
    logger.addHandler(console_handler)

    return logger


# Create the logger instance
# Other files import this directly
logger = setup_logging()