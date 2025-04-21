import logging

from mkdocs.commands import build
from mkdocs import config


log = logging.getLogger(__name__)


def main(**kwargs):
    """Build the MkDocs documentation and start MCP Server."""

    cfg = config.load_config(**kwargs)
    cfg.plugins.on_startup(command="build", dirty=False)
    try:
        build.build(cfg)
    finally:
        cfg.plugins.on_shutdown()

    from rich import inspect

    inspect(cfg.plugins)
    inspect(cfg.plugins.get("mcp"))


if __name__ == "__main__":
    main()
