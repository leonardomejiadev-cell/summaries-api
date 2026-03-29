import logging


def configure_logging() -> None:
    """Configura el logging global de la aplicación."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
