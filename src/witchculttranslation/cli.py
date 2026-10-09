import logging
from pathlib import Path

import click

from witchculttranslation.epub import EpubWriter, read_epub, write_epub
from witchculttranslation.exceptions import ApplicationException, NotFound
from witchculttranslation.interactors.download_chapter import (
    DownloadChapter,
    DownloadChapterDTO,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
ROOT = Path(__file__).parent.parent.parent


@click.command("download-rezero-chapter")
@click.option(
    "--book",
    "book_path",
    default=None,
    help="Existing Epub book path, chapter will be added to it",
    type=Path,
)
@click.option("--url", help="URL of the `witchculttranslation` chapter")
@click.option("--output", help="Path for the book output", default=None)
def download_rezero_chapter(
    book_path: Path | None,
    url: str,
    output: Path | None,
) -> None:
    if not url:
        logger.error(msg := "URL cannot be empty")
        raise click.BadOptionUsage("--url", msg)
    logger.info("Download chapter: url=%s, book_path=%s", url, book_path)

    title = "Re:Zero − Starting Life in Another World: Web novel"

    if book_path:
        book = read_epub(book_path)
        title = str(book.title) or title
        new_book: bool = False
    else:
        book_path = output or ROOT / f"{title}.epub"
        new_book = True
        book = EpubWriter.create_book(
            author="Tappei Nagatsuki and witchculttranslation team",
            title=title,
        )
        write_epub(book_path, book)

    download_chapter = DownloadChapter()

    try:
        chapter = download_chapter(DownloadChapterDTO(url=url, book_path=book_path))
    except NotFound as e:
        raise click.BadOptionUsage(
            "url", f"URL for the chapter is invalid: {e.message}"
        )
    except ApplicationException as e:
        raise click.BadOptionUsage("url", e.message)

    if new_book and chapter.images:
        logger.info("Setting cover image for new EPUB book")
        book = read_epub(book_path)
        cover_file_name = list(chapter.images)[0]

        EpubWriter(book).book.set_cover(
            file_name=f"cover_{cover_file_name}",
            content=chapter.images[cover_file_name],
            create_page=False,
        )

        write_epub(book_path, book)

    logger.info("Saved result to %s", str(book_path))


if __name__ == "__main__":
    download_rezero_chapter()
