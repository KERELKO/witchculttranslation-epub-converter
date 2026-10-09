from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from witchculttranslation.html_parsing import download_chapter
from witchculttranslation.epub import EpubWriter, read_epub, write_epub
from witchculttranslation.dto import Chapter


logger = getLogger(__name__)


@dataclass(slots=True)
class DownloadChapterDTO:
    url: str
    book_path: Path


class DownloadChapter:
    """Extends EPUB book with new chapter by downloading it from `witchculttranslation` page"""

    def __init__(self, html_parser: str = "html.parser") -> None:
        self.html_parser = html_parser

    def __call__(self, data: DownloadChapterDTO) -> Chapter:
        logger.info("Download chapter: url=%s, book_path=%s", data.url, data.book_path)

        chapter = download_chapter(data.url, self.html_parser)

        book = read_epub(data.book_path)

        epub_writer = EpubWriter(book)
        epub_writer.add_chapter(chapter)

        write_epub(data.book_path, book)

        logger.info(
            "Updated EPUB book with new chapter and saved to %s", str(data.book_path)
        )

        return chapter
