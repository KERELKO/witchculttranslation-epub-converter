from enum import Enum, auto
from typing import cast

import bs4  # type: ignore[import-untyped]

from witchculttranslation.dto import Arc, Phase, PhaseChapter


class ParsingState(Enum):
    ARC = auto()
    COVER = auto()
    PHASE = auto()
    CHAPTER = auto()

    def next_state(self) -> "ParsingState":
        """Returns next state of Parsing State. `ARC -> COVER -> PHASE -> CHAPTER -> PHASE`"""
        mapping = {
            self.ARC: self.COVER,
            self.COVER: self.PHASE,
            self.PHASE: self.CHAPTER,
            self.CHAPTER: self.PHASE,
        }
        return mapping[self]  # type: ignore[return-value, index]

    def reset(self) -> "ParsingState":
        return self.ARC  # type: ignore[return-value]


def is_style_tag(tag: bs4.Tag) -> bool:
    """Returns `True` if tag does not provide any useful information and only appears as style tag"""
    if tag.name in ("hr",):
        return True

    if tag.name in ("p", "h1"):
        if tag.img:
            return False

        if not tag.get_text(strip=True):
            return True

    return False


def is_arc_tag(tag: bs4.Tag) -> bool:
    if tag.name != "h1":
        return False

    if "arc" not in tag.text.strip().lower():
        return False
    return True


def is_phase_tag(tag: bs4.Tag) -> bool:
    # It's not accurate at all, but there is no other way to identify if tag is a `Phase tag`.
    # Some additional checks should exist before using this function
    return tag.name == "h1"


def is_side_content(tag: bs4.Tag) -> bool:
    return tag.name == "h1" and tag.text == "Side Content"


def parse_toc(html: bs4.BeautifulSoup) -> list[Arc]:
    """Parses `table-of-content` witchculttranslation HTML page and extracts all information about arcs"""
    article = html.find("article")

    entry_content = cast(bs4.Tag, article.find(class_="entry-content"))  # type: ignore[union-attr]

    arcs: list[Arc] = []
    parsing_stage = ParsingState.ARC

    tags = entry_content.find_all(lambda x: x.name in ("h1", "ul", "p"))
    current_tag_idx = 0

    while current_tag_idx < len(tags):
        tag = tags[current_tag_idx]

        if is_style_tag(tag):
            current_tag_idx += 1
            continue

        if is_side_content(tag):
            break

        match parsing_stage:
            case ParsingState.ARC:
                if not is_arc_tag(tag):
                    current_tag_idx += 1
                    continue

                arc = Arc(name=tag.text)
                parsing_stage = parsing_stage.next_state()
                arcs.append(arc)
                current_tag_idx += 1

            case ParsingState.COVER:
                if tag.img:
                    arc.cover_url = str(tag.img.attrs["src"])
                    current_tag_idx += 1
                    continue

                if tag.name != "p":
                    parsing_stage = parsing_stage.next_state()
                    continue

                arc = arcs[-1]

                if tag.text:
                    note = tag.text.strip()
                    arc.note = "\n".join([arc.note, note] if arc.note else [note])

                current_tag_idx += 1

            case ParsingState.PHASE:
                if is_arc_tag(tag):
                    parsing_stage = parsing_stage.reset()
                    continue

                arc = arcs[-1]

                if tag.name == "p" and tag.text:
                    note = tag.text.strip()
                    arc.note = "\n".join([arc.note, note] if arc.note else [note])
                    current_tag_idx += 1
                    continue

                if not is_phase_tag(tag):
                    parsing_stage = parsing_stage.next_state()
                    continue

                arc.phases.append(Phase(name=tag.text.strip(), arc_name=arc.name))
                parsing_stage = parsing_stage.next_state()
                current_tag_idx += 1

            case ParsingState.CHAPTER:
                if tag.name != "ul":
                    parsing_stage = parsing_stage.next_state()
                    continue

                arc = arcs[-1]
                arc.add_default_phase()

                phase = arc.phases[-1]

                li_tags = tag.find_all("li")
                phase.total_chapters = len(li_tags)

                for li_tag in li_tags:
                    phase_chapter = PhaseChapter(name="", url=None, note="")

                    a_tag = li_tag.find("a")

                    if a_tag:
                        phase_chapter.name = a_tag.text
                        phase_chapter.url = str(a_tag.attrs["href"])
                        phase_chapter.note = getattr(li_tag, "text", None)
                    else:
                        phase_chapter.name = (
                            getattr(li_tag, "text", None) or "Unknown chapter"
                        )
                        phase_chapter.note = "Failed to download this chapter"
                    phase.chapters.append(phase_chapter)

                parsing_stage = parsing_stage.next_state()
                current_tag_idx += 1
    return arcs
