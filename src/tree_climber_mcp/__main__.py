import asyncio
import logging
import sys

from .server import TreeClimberServer


def setup_logging(level: str = "INFO") -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


async def main() -> None:
    setup_logging("INFO")
    logger = logging.getLogger(__name__)

    try:
        server = TreeClimberServer(logger)
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user...")
    except Exception as exc:
        logger.error("Server error: %s", exc)
        sys.exit(1)


def cli() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli()
