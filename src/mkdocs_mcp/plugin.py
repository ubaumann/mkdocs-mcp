from typing import TYPE_CHECKING, Optional
import logging
from dataclasses import dataclass
from pathlib import Path

from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.structure.files import InclusionLevel

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files


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

    def on_post_build(self, config: "MkDocsConfig") -> None:
        # ToDo: Should we convert the html to markdown using BeautifulSoup?
        ...

    def on_files(self, files: "Files", *, config: "MkDocsConfig") -> Optional["Files"]:
        """Populate md_pages"""
        for name, f in files.src_paths.items():
            # Only use "included" files to ignore generated files like .css, .js, .woff2, ...
            if f.inclusion.value == InclusionLevel.INCLUDED.value:
                self.md_pages[name] = PageInfo(
                    title=name,  # ToDo
                    path_md=Path(f.abs_src_path if f.abs_src_path else "not found"),
                    content=f.content_string,
                )

        return files
