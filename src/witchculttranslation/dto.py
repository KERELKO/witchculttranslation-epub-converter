from dataclasses import dataclass, field


@dataclass(slots=True)
class Chapter:
    title: str
    authors: list[str]
    posted_info: str
    translated_by: list[str]
    chapter_html: str
    images: dict[str, bytes] = field(default_factory=dict)
