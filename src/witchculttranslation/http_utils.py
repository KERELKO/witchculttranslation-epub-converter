from dataclasses import dataclass
from logging import getLogger
import mimetypes

import requests

from witchculttranslation.exceptions import ApplicationException, NotFound

logger = getLogger(__name__)


@dataclass(slots=True)
class Response:
    content: bytes
    content_type: str

    @property
    def content_extension(self) -> str:
        ext = mimetypes.guess_extension(self.content_type) or ".jpg"

        if ext == ".jpe":
            ext = ".jpg"
        return ext

    @property
    def text(self) -> str:
        media_type = self.content_type.split(";", 1)[0].strip().lower()
        if not (
            media_type.startswith("text/")
            or media_type
            in {"application/json", "application/xml", "application/xhtml+xml"}
        ):
            raise ApplicationException(
                "Response content type is not textual: %s" % self.content_type
            )

        return self.content.decode("utf-8")


def get_response(url: str) -> Response:
    logger.info("Make request to %s", url)
    response = requests.get(url, timeout=15)

    if response.status_code == 404:
        raise NotFound("URL is invalid")

    if not response.ok:
        msg = f"Request to {url} failed with {response.status_code} status code"
        logger.error(msg)
        raise ApplicationException(msg)

    return Response(
        content=response.content, content_type=response.headers.get("Content-Type", "")
    )
