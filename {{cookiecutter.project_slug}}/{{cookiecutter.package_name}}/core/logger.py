"""Contain helpers to customize logging for the service."""
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from types import FrameType

    import loguru


class _InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        # Find caller from where originated the logging call
        frame: "FrameType" | None = logging.currentframe()
        depth: int = 2

        while frame is not None and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id="app")
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def customize_logging(
    filepath: Path, level: str, rotation: str, retention: str, _format: str
) -> "loguru.Logger":
    """Define the logger to be used by the service based on loguru."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        level=level.upper(),
        format=_format,
        colorize=True,
    )
    logger.add(
        str(filepath),
        rotation=rotation,
        retention=retention,
        enqueue=True,
        backtrace=True,
        level=level.upper(),
        format=_format,
    )
    logging.basicConfig(handlers=[_InterceptHandler()], level=0)
    for _log in [
        "uvicorn",
        "uvicorn.error",
        "fastapi",
        "sqlalchemy",
        "databases",
        "alembic",
    ]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [_InterceptHandler()]

    return logger.bind(request_id="app")


__all__ = [
    "customize_logging",
]
