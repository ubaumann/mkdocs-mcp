from typing import TYPE_CHECKING
import logging
from dataclasses import dataclass
from pathlib import Path

from html2text import html2text

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
    naming_style = config_options.Choice(
        (
            "src_file",
            "dst_url",
            "title",
        ),
        default="src_file",
    )
    prefer_markdown = config_options.Type(bool, default=True)
    combine_all_pages = config_options.Type(bool, default=False)


class MkDocsMCP(BasePlugin[MkDocsMCPConfig]):
    """The MkDocs plugin keeps track of pages,
    allowing to use the mapping to serve resources with a MCP server.

    This plugin defines the following event hooks:

    - `on_post_page`


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
        markdown = page.markdown
        file_path = page.file.src_uri

        match self.config.get("naming_style"):
            case "src_file":
                title = file_path
            case "dst_url":
                title = page.abs_url or ""
            case "title":
                title = page.title

        if self.config.get("prefer_markdown") and markdown:
            content = markdown
        else:
            content = html2text(output)

        if self.config.get("combine_all_pages"):
            aggregated_page = self.md_pages.get(
                "all", PageInfo(title="", path_md=Path("."), content="")
            )
            aggregated_page.content = aggregated_page.content + content + "\n"
            self.md_pages["all"] = aggregated_page

        self.md_pages[file_path] = PageInfo(
            title=title,
            path_md=Path(file_path),
            content=content,
        )
        return output
