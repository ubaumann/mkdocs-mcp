import logging

from mkdocs.commands import build
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


def main(**kwargs):
    """Build the MkDocs documentation and start MCP Server."""

    cfg = config.load_config(**kwargs)
    cfg.plugins.on_startup(command="build", dirty=False)
    try:
        build.build(cfg)
    finally:
        cfg.plugins.on_shutdown()

    mcp_plugin = cfg.plugins.get("mcp")

    # mcp.name = cfg.site_name
    for _, page in mcp_plugin.md_pages.items():
        add_resource(mcp, page)

    mcp.run()


if __name__ == "__main__":
    main()
