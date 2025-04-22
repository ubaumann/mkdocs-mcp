import logging

import click
from mkdocs.commands import build
from mkdocs.__main__ import (
    common_config_options,
    common_options,
    cli,
    clean_help,
    site_dir_help,
)
from mkdocs import config

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import FunctionResource
from pydantic.networks import AnyUrl

from mkdocs_mcp.plugin import PageInfo


log = logging.getLogger(__name__)
mcp = FastMCP()


def add_resource(mcp: FastMCP, page: PageInfo) -> None:
    # Register as regular resource
    resource = FunctionResource(
        uri=AnyUrl(f"docs://{page.title}"),
        name=page.title,
        description=f"The {page.title} documentation",
        mime_type="text/markdown",
        fn=lambda: page.content,
    )
    mcp.add_resource(resource=resource)


@cli.command(name="build")
@click.option(
    "-mt",
    "--mcp-transport",
    type=click.Choice(["stdio", "sse"]),
    help="MCP mode",
    default="stdio",
)
@click.option("-c", "--clean/--dirty", is_flag=True, default=True, help=clean_help)
@common_config_options
@click.option("-d", "--site-dir", type=click.Path(), help=site_dir_help)
@common_options
def build_and_mcp(mcp_transport, clean, **kwargs):
    """Build the MkDocs documentation and start MCP Server."""

    cfg = config.load_config(**kwargs)
    cfg.plugins.on_startup(command="build", dirty=not clean)
    try:
        build.build(cfg)
    finally:
        cfg.plugins.on_shutdown()

    mcp_plugin = cfg.plugins.get("mcp")

    mcp._mcp_server.name = cfg.site_name
    log.info("Starting adding resources to MCP")
    for name, page in mcp_plugin.md_pages.items():
        add_resource(mcp, page)
        log.debug(f"Adding resource {name} to MCP")

    log.info("Starting MCP server")
    mcp.run(mcp_transport)


if __name__ == "__main__":
    build_and_mcp()
