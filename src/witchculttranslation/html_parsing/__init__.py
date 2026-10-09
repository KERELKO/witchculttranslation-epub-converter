"""Package for parsing HTML pages of witchculttranslation page.
* `chapter` - parsing individual chapter page with full chapter content
* `toc` - parsing `table-of-content` witchculttranslation web page.
"""

from .chapter import download_chapter
from .toc import parse_toc

__all__ = ["download_chapter", "parse_toc"]
