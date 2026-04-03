import argparse
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tree_climber_mcp import __main__


def test_parse_args_defaults_to_restricted_cwd():
    args = __main__.parse_args([])

    assert args.allow_all_paths is False
    assert args.filesystem_root is None


def test_parse_args_accepts_allow_all_paths():
    args = __main__.parse_args(["--allow-all-paths"])

    assert args.allow_all_paths is True
    assert args.filesystem_root is None


def test_parse_args_accepts_filesystem_root():
    args = __main__.parse_args(["--filesystem-root", "../shared"])

    assert args.allow_all_paths is False
    assert args.filesystem_root == "../shared"


def test_parse_args_rejects_conflicting_filesystem_flags():
    with pytest.raises(SystemExit) as exc_info:
        __main__.parse_args(["--allow-all-paths", "--filesystem-root", "/tmp"])

    assert exc_info.value.code == 2


@pytest.mark.asyncio
async def test_main_passes_resolved_filesystem_root_to_server():
    logger = MagicMock()
    with (patch("tree_climber_mcp.__main__.setup_logging"),
          patch("tree_climber_mcp.__main__.logging.getLogger", return_value=logger),
          patch("tree_climber_mcp.__main__.TreeClimberServer") as mock_server_cls,
          patch("tree_climber_mcp.__main__.os.path.realpath", return_value="/trusted/root")):
        mock_server = AsyncMock()
        mock_server_cls.return_value = mock_server

        await __main__.main(["--filesystem-root", "../shared"])

    mock_server_cls.assert_called_once_with(
        logger,
        allow_all_paths=False,
        filesystem_root="/trusted/root",
    )
    mock_server.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_passes_allow_all_paths_to_server():
    logger = MagicMock()
    with (patch("tree_climber_mcp.__main__.setup_logging"),
          patch("tree_climber_mcp.__main__.logging.getLogger", return_value=logger),
          patch("tree_climber_mcp.__main__.TreeClimberServer") as mock_server_cls):
        mock_server = AsyncMock()
        mock_server_cls.return_value = mock_server

        await __main__.main(["--allow-all-paths"])

    mock_server_cls.assert_called_once_with(
        logger,
        allow_all_paths=True,
        filesystem_root=None,
    )
    mock_server.run.assert_awaited_once()
