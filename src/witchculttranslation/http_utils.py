from dataclasses import dataclass
from logging import getLogger
import mimetypes
from typing import Any

import requests

from witchculttranslation.exceptions import ApplicationException

logger = getLogger(__name__)


@dataclass
class Response:
    content: Any
    content_type: str

    @property
    def content_extension(self) -> str:
        ext = mimetypes.guess_extension(self.content_type) or '.jpg'

        if ext == '.jpe':
            ext = '.jpg'
        return ext


def get_response(url: str) -> Response:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return Response(
        content=response.content,
        content_type=response.headers.get("Content-Type", '')
    )


def parse_witchculttranslation_page(url: str) -> str:
    logger.info("Make request to %s", url)
    response = requests.get(url)

    if not response.ok:
        msg = f"Request to {url} failed with {response.status_code} status code"
        logger.error(msg)
        raise ApplicationException(msg)

    return response.text
