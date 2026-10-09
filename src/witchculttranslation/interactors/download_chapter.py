from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

import bs4  # type: ignore[import-untyped]

from witchculttranslation.content_extractor import (
    download_and_replace_images,
    extract_chapter,
    get_image_links,
    normalize_chapter_html,
)
from witchculttranslation.epub import EpubWriter, read_epub, write_epub
from witchculttranslation.http_utils import parse_witchculttranslation_page
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

        witchculttranslation_html_page = parse_witchculttranslation_page(data.url)

        witchculttranslation_html_page_soup = bs4.BeautifulSoup(
            witchculttranslation_html_page, self.html_parser
        )
        chapter = extract_chapter(witchculttranslation_html_page_soup)

        chapter_html = bs4.BeautifulSoup(chapter.chapter_html, self.html_parser)

        image_links = get_image_links(chapter_html)

        normalize_chapter_html(chapter_html)
        downloaded_images = download_and_replace_images(chapter_html, image_links)

        chapter.chapter_html = str(chapter_html)
        chapter.images = downloaded_images

        book = read_epub(data.book_path)

        epub_writer = EpubWriter(book)
        epub_writer.add_chapter(chapter)

        write_epub(data.book_path, book)

        logger.info(
            "Updated EPUB book with new chapter and saved to %s", str(data.book_path)
        )

        return chapter
