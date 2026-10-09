from logging import getLogger
from typing import cast
import uuid

import bs4  # type: ignore[import-untyped]

from witchculttranslation.dto import Chapter
from witchculttranslation.exceptions import ApplicationException
from witchculttranslation.http_utils import get_response

logger = getLogger(__name__)


def _extract_chapter(html: bs4.BeautifulSoup | bs4.Tag) -> Chapter:
    """Extracts `witchculttranslation` HTML page content and extracts content of a chapter"""

    article = html.find("article")

    if not article:
        msg = "Failed to find chapter content for provided HTML"
        logger.error(msg)
        raise ApplicationException(msg)

    title_tag = article.find("h1", class_="entry-title")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

    authors = []
    post_by_tag = article.find("span", class_="post-by")
    if post_by_tag:
        authors = [
            a.get_text(strip=True) for a in post_by_tag.find_all("a", class_="url")
        ]

    posted_info = ""
    poston_tag = article.find("span", class_="poston")
    if poston_tag:
        pub_time = poston_tag.find("time", class_="entry-date published")
        if pub_time:
            posted_info = pub_time.get_text(strip=True)
        else:
            posted_info = poston_tag.get_text(strip=True)

    translated_by = []
    t_by_tag = article.find(
        lambda tag: tag.name == "p" and "Translated By:" in tag.get_text()
    )
    if t_by_tag:
        ul_tag = t_by_tag.find_next_sibling("ul")
        if ul_tag:
            translated_by = [li.get_text(strip=True) for li in ul_tag.find_all("li")]

    return Chapter(
        title=title,
        authors=authors,
        posted_info=posted_info,
        translated_by=translated_by,
        chapter_html=str(article),
        url="",
    )


def _get_image_links(html: bs4.BeautifulSoup | bs4.Tag) -> list[str]:
    """
    Finds all image links in the soup, and returns their URLs
    """
    image_links: list[str] = []

    for img_tag in html.find_all("img"):
        original_url = img_tag.get("src")

        if not original_url or not (url_val := str(original_url)).startswith("http"):
            continue

        image_links.append(url_val)
    return image_links


UNSUPPORTED_STRINGS = frozenset({"△▼△▼△▼△"})
WHITESPACE_CHARS = frozenset({" ", "\t", "\n", "\r", "\xa0", "\u3000"})
DECORATIVE_ONLY_CHARS = frozenset({"△", "▼"})


def _download_and_replace_images(
    html: bs4.BeautifulSoup | bs4.Tag,
    image_links: list[str],
) -> dict[str, bytes]:
    """Find all images from provided list in HTML, downloads them and replaces in HTML tree.
    Returns images mapping.
    """
    images: dict[str, bytes] = {}
    for image_url in image_links:
        try:
            logger.info("Download image by '%s'", image_url)
            response = get_response(image_url)
        except Exception as e:
            logger.error(
                "Failed to download image by URL '%s': message=%s", image_url, e
            )
            continue

        tags = html.find_all("img", attrs={"src": image_url})
        internal_filename = f"img_{uuid.uuid4().hex[:8]}{response.content_extension}"
        images[internal_filename] = response.content

        for img_tag in tags:
            img_tag["src"] = internal_filename

            attrs_to_remove = [
                "srcset",
                "sizes",
                "loading",
                "fetchpriority",
                "decoding",
                "class",
                "style",
            ]
            for attr in attrs_to_remove:
                if img_tag.has_attr(attr):
                    del img_tag[attr]
    return images


def _normalize_chapter_html(html: bs4.BeautifulSoup | bs4.Tag) -> None:
    for paragraph in html.find_all("p"):
        paragraph = cast(bs4.Tag, paragraph)

        if paragraph.img:
            continue

        paragraph_text = paragraph.get_text()
        compact_text = "".join(
            char for char in paragraph_text if char not in WHITESPACE_CHARS
        )

        if not compact_text:
            paragraph.decompose()
            continue

        if any(
            unsupported_string in compact_text
            for unsupported_string in UNSUPPORTED_STRINGS
        ):
            paragraph.decompose()
            continue

        if all(char in DECORATIVE_ONLY_CHARS for char in compact_text):
            paragraph.decompose()


def download_chapter(url: str, html_parser: str) -> Chapter:
    """Downloads chapter HTML from URL, processes and return instance of `Chapter`"""
    logger.info("Download chapter: url=%s", url)

    witchculttranslation_html_page = get_response(url).text

    witchculttranslation_html_page_soup = bs4.BeautifulSoup(
        witchculttranslation_html_page, html_parser
    )
    chapter = _extract_chapter(witchculttranslation_html_page_soup)
    chapter.url = url

    chapter_html = bs4.BeautifulSoup(chapter.chapter_html, html_parser)

    image_links = _get_image_links(chapter_html)

    _normalize_chapter_html(chapter_html)
    downloaded_images = _download_and_replace_images(chapter_html, image_links)

    chapter.chapter_html = str(chapter_html)
    chapter.images = downloaded_images

    return chapter
