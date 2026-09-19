"""The server's own identity: name, version, and that every tool is a thin wrapper.

The version test is a regression test. FastMCP does not accept a version argument, so the version
was unset and serverInfo reported the `mcp` SDK's version instead -- a client asking what version
of bible-references it was talking to got "1.28.1", a number that moves when the SDK is upgraded
and never moves when a tool is added or changed.
"""
import tomllib
from pathlib import Path

import mcp_server

BUILD_DIR = Path(__file__).resolve().parent.parent


def _pyproject_version() -> str:
    with open(BUILD_DIR / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


def _server_info():
    return mcp_server.mcp._mcp_server.create_initialization_options()


def test_server_reports_its_own_version_not_the_sdks():
    info = _server_info()
    assert info.server_version == _pyproject_version()


def test_reported_version_is_not_the_mcp_package_version():
    """The exact failure this guards: serverInfo answering with the SDK's version."""
    from importlib.metadata import version
    assert _server_info().server_version != version("mcp")


def test_server_name_is_stable():
    """Clients key their config on this; renaming it breaks every configured host."""
    assert _server_info().server_name == "bible-references"


def test_instructions_name_the_entry_point_and_the_silent_failures():
    text = mcp_server.mcp.instructions
    assert "passage_brief" in text
    assert "study-notes.db" in text
    assert "never" in text.lower() and "memory" in text.lower()
