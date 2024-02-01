import os
import logging.handlers
from typing import Final

LOG_FORMAT: Final = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_TIME_FMT: Final = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL: Final = "debug"


def get_log_level(log_level_env: str) -> int:
    """Get log level from env var and convert it to a corresponding integer."""
    supported_levels: dict[str, int] = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }
    env_value = log_level_env.strip().lower()
    if env_value not in supported_levels.keys():
        raise RuntimeError(
            f"Invalid LOG_LEVEL={env_value}. Supported levels are {'|'.join(supported_levels)}."
        )
    return supported_levels[env_value]


def build_logger(name: str):
    """Easy to use logger with handlers configured."""

    log_level = get_log_level(os.environ.get("LOG_LEVEL", DEFAULT_LOG_LEVEL))
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(
        logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_TIME_FMT)
    )

    logger.addHandler(stream_handler)

    return logger
