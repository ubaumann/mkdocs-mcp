from typing import TYPE_CHECKING
import logging
from dataclasses import dataclass
from pathlib import Path

from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.config.base import Config

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.pages import Page


log = logging.getLogger(__name__)


@dataclass
class PageInfo:
    """Class to store page information"""

    title: str
    path_md: Path
    content: str


class MkDocsMCPConfig(Config):
    foo = config_options.Type(str, default="a default value")
    bar = config_options.Type(int, default=0)
    baz = config_options.Type(bool, default=True)


class MkDocsMCP(BasePlugin[MkDocsMCPConfig]):
    """The MkDocs plugin keeps track of pages,
    allowing to use the mapping to serve resources with a MCP server.

    This plugin defines the following event hooks:

    - `on_page_content`
    - `on_post_build`


    """

    md_pages: dict[str, PageInfo] = {}
    """Dictionary mapping section names to a list of page infos."""

    def on_post_page(
        self, output: str, /, *, page: "Page", config: "MkDocsConfig"
    ) -> str | None:
        """
        The `post_page` event is called after the template is rendered, but
        before it is written to disc and can be used to alter the output of the
        page. If an empty string is returned, the page is skipped and nothing is
        written to disc.

        Args:
            output: output of rendered template as string
            page: `mkdocs.structure.pages.Page` instance
            config: global configuration object

        Returns:
            output of rendered template as string
        """
        title = page.title
        markdown = page.markdown
        file_path = page.file.src_uri

        self.md_pages[file_path] = PageInfo(
            title=title,
            path_md=Path(file_path),
            content=str(markdown),
        )
        return output
