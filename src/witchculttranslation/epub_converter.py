from logging import getLogger
import mimetypes
import uuid

from ebooklib import epub  # type: ignore[import-untyped]

from witchculttranslation.dto import Arc
from witchculttranslation.exceptions import ApplicationException  # type: ignore[import-untyped]

logger = getLogger(__name__)


DEFAULT_EBOOK_STYLES = """
@namespace epub "http://www.idpf.org/2007/ops";
body { font-family: sans-serif; margin: 2px; padding: 0; }
h1 { font-size: 1.2em; text-align: center; margin-top: 5px; }
p { text-indent: 1em; line-height: 1.3; margin-bottom: 5px; }
"""
DEFAULT_STYLES_ID = "style_default"


class EpubWriter:
    def __init__(self, book: epub.EpubBook) -> None:
        self.book = book

        if not (default_styles := self.book.get_item_with_id(DEFAULT_STYLES_ID)):
            logger.error(msg := "Ebook does not have default styles")
            raise ApplicationException(msg)

        self.default_styles = default_styles
        self._ensure_toc_uids(self.book.toc)

    def _ensure_toc_uids(self, toc_items: list | tuple, prefix: str = "toc") -> None:
        for index, toc_item in enumerate(toc_items):
            if isinstance(toc_item, (list, tuple)):
                self._ensure_toc_uids(toc_item, f"{prefix}-{index}")
                continue

            if getattr(toc_item, "uid", None):
                continue

            toc_item.uid = getattr(toc_item, "href", None) or f"{prefix}-{index}"

    @classmethod
    def create_book(
        cls,
        author: str,
        title: str,
        language: str = "en",
        cover: tuple[str, bytes] | None = None,
    ) -> epub.EpubBook:
        logger.info("Create new Epub book '%s'", title)
        book = epub.EpubBook()
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(title)
        book.set_language(language)
        book.add_author(author)

        styles = epub.EpubItem(
            uid=DEFAULT_STYLES_ID,
            file_name="style/default.css",
            media_type="text/css",
            content=DEFAULT_EBOOK_STYLES,
        )

        book.add_item(styles)

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.toc = []
        book.spine = ["nav"]

        if cover:
            book.set_cover(file_name=cover[0], content=cover[1], create_page=False)

        return book

    def add_arc(self, arc: Arc) -> epub.EpubHtml:
        current_arc = len(self.book.toc)
        file_name = f"arc_{current_arc}.xhtml"
        logger.info("Add new arc '%s', with file name '%s'", arc.title, file_name)

        for internal_path, img_bytes in arc.images.items():
            logger.info("Adding image '%s'", internal_path)
            mime_type, _ = mimetypes.guess_type(internal_path)

            img_item = epub.EpubImage(
                uid=internal_path,
                file_name=internal_path,
                media_type=mime_type or "image/jpeg",
                content=img_bytes,
            )
            self.book.add_item(img_item)

        new_arc = epub.EpubHtml(
            uid=file_name,
            title=arc.title,
            file_name=file_name,
            lang=self.book.language,
            content=arc.arc_html,
        )
        new_arc.add_item(self.default_styles)

        self.book.add_item(new_arc)
        self.book.toc.append(new_arc)
        self.book.spine.append(new_arc)

        return new_arc
