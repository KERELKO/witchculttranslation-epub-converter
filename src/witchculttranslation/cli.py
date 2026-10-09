import logging
from pathlib import Path

import bs4
import click
from ebooklib import epub  # type: ignore[import-untyped]

from witchculttranslation.content_extractor import download_and_replace_images, extract_arc, get_image_links, normalize_arc_html
from witchculttranslation.epub_converter import EpubWriter
from witchculttranslation.http_utils import parse_witchculttranslation_page

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


@click.command("download-rezero-arc")
@click.option(
    "--book", "book_path",
    default=None,
    help="Existing Epub book path, chapter will be added to it",
    type=Path,
)
@click.option("--url", help="URL of the `witchculttranslation` arc")
@click.option("--output", help="Path for the book output", default=None)
def download_rezero_arc(
    book_path: Path | None,
    url: str,
    output: Path | None,
) -> None:
    if not url:
        logger.error(msg := "URL cannot be empty")
        raise click.BadOptionUsage("--url", msg)
    logger.info("Download arc: url=%s, book_path=%s", url, book_path)

    witchculttranslation_html_page = parse_witchculttranslation_page(url)

    soup = bs4.BeautifulSoup(witchculttranslation_html_page, "html.parser")
    arc = extract_arc(soup)

    arc_html = bs4.BeautifulSoup(arc.arc_html, "html.parser")

    image_links = get_image_links(arc_html)    

    normalize_arc_html(arc_html)
    downloaded_images = download_and_replace_images(arc_html, image_links)

    arc.arc_html = str(arc_html)
    arc.images = downloaded_images

    title = "Re:Zero − Starting Life in Another World: Web novel"

    if book_path:
        book = epub.read_epub(book_path)
    else:
        cover_file_name = list(arc.images)[0]
        book = EpubWriter.create_book(
            author="Tappei Nagatsuki and witchculttranslation team",
            title=title,
            cover=(f"cover_{cover_file_name}", arc.images[cover_file_name])
        )

    epub_writer = EpubWriter(book)
    epub_writer.add_arc(arc)

    result_path = output or book_path or Path(__file__).parent / f"{title}.epub"
    epub.write_epub(result_path, book)

    logger.info("Saved result to %s", str(result_path))


if __name__ == '__main__':
    download_rezero_arc()
