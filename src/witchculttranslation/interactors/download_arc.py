from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from witchculttranslation.constants import AUTHORS
from witchculttranslation.dto import Arc
from witchculttranslation.html_parsing.chapter import download_chapter
from witchculttranslation.http_utils import get_response
from witchculttranslation.progress_bar import ProgressBar
from witchculttranslation.epub import write_epub, EpubWriter

logger = getLogger(__name__)


@dataclass(slots=True)
class DownloadArcDTO:
    arc: Arc
    result_path: Path


class DownloadArc:
    def __init__(
        self,
        progress_bar: ProgressBar,
        html_parser: str = "html.parser",
    ) -> None:
        self.html_parser = html_parser
        self.progress_bar = progress_bar

    def __call__(self, data: DownloadArcDTO) -> Path:
        logger.info("Download arc '%s'", data.arc.name)

        cover: tuple[str, bytes] | None = None
        if data.arc.cover_url:
            cover_response = get_response(data.arc.cover_url)
            cover = (
                f"cover_{data.arc.name}.{cover_response.content_extension}",
                cover_response.content,
            )

        book = EpubWriter.create_book(
            author=AUTHORS,
            title=f"Re:Zero {data.arc.name}",
            cover=cover,
        )

        epub_writer = EpubWriter(book)

        with self.progress_bar as bar:
            for phase in data.arc.phases:
                for phase_chapter in phase.chapters:
                    if not phase_chapter.url:
                        logger.warning(
                            "Chapter does not have URL: arc=%s, phase=%s, chapter_name=%s, note=%s",
                            data.arc.name,
                            phase.name,
                            phase_chapter.name,
                            phase_chapter.note,
                        )
                        continue
                    chapter = download_chapter(phase_chapter.url, self.html_parser)
                    epub_writer.add_chapter(chapter)
                    bar.update(1)

        write_epub(data.result_path, epub_writer.book)
        return data.result_path
