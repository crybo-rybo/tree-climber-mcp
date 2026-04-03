import argparse
import asyncio
import logging
import os
import sys

from .server import TreeClimberServer


def setup_logging(level: str = "INFO") -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Tree Climber MCP server."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--allow-all-paths",
        action="store_true",
        help="Disable filesystem path restrictions for read, write, and list tools.",
    )
    group.add_argument(
        "--filesystem-root",
        help="Restrict filesystem tools to this root instead of the shell working directory.",
    )
    return parser.parse_args(argv)


async def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    setup_logging("INFO")
    logger = logging.getLogger(__name__)
    filesystem_root = (
        os.path.realpath(args.filesystem_root) if args.filesystem_root else None
    )

    try:
        server = TreeClimberServer(
            logger,
            allow_all_paths=args.allow_all_paths,
            filesystem_root=filesystem_root,
        )
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user...")
    except Exception as exc:
        logger.error("Server error: %s", exc)
        sys.exit(1)


def cli(argv: list[str] | None = None) -> None:
    try:
        asyncio.run(main(argv))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli(sys.argv[1:])
