from dataclasses import dataclass, field


@dataclass(slots=True)
class Chapter:
    title: str
    authors: list[str]
    posted_info: str
    translated_by: list[str]
    chapter_html: str
    url: str
    images: dict[str, bytes] = field(default_factory=dict)


@dataclass(slots=True)
class PhaseChapter:
    """Chapter that references to a phase providing meta information regarding chapter content"""

    name: str
    note: str | None
    url: str | None


@dataclass(slots=True)
class Phase:
    name: str
    arc_name: str
    total_chapters: int = 0
    note: str | None = None
    chapters: list[PhaseChapter] = field(default_factory=list)


@dataclass(slots=True)
class Arc:
    name: str
    phases: list[Phase] = field(default_factory=list)
    """Phases of an Arc"""
    cover_url: str | None = None
    note: str | None = None

    def add_default_phase(self) -> None:
        """Adds default phase for arc if arc does not have any phases"""
        if not self.phases:
            self.phases.append(Phase(name="Phase 1", arc_name=self.name))
