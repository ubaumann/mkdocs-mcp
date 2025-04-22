import pytest
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import Resource


from mkdocs_mcp.__main__ import add_resource
from mkdocs_mcp.plugin import PageInfo


@pytest.fixture
def mcp_app() -> FastMCP:
    return FastMCP()


@pytest.fixture
def pages() -> list[PageInfo]:
    return [
        PageInfo(
            title="index", path_md=Path("./index.md"), content="# Title\n\nmore text"
        ),
        PageInfo(
            title="about", path_md=Path("./about.md"), content="# About\n\nmore text"
        ),
    ]


@pytest.fixture
def mcp_resources(mcp_app, pages) -> list[Resource]:
    add_resource(mcp_app, pages[0])
    add_resource(mcp_app, pages[1])
    return list(mcp_app._resource_manager._resources.values())


def test_add_resource_len(mcp_resources) -> None:
    assert len(mcp_resources) == 2


@pytest.mark.parametrize("i", [0, 1])
def test_add_resource_title(mcp_resources, pages, i) -> None:
    assert mcp_resources[i].name == pages[i].title
