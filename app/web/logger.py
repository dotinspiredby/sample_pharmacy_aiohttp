import logging
import typing
if typing.TYPE_CHECKING:
    from .app_ import Application


def setup_logging(_: "Application") -> None:
    logging.basicConfig(level=logging.INFO)
