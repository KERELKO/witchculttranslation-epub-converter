from logging import getLogger
from pathlib import Path

import bs4  # type: ignore[import-untyped]
import click
import questionary  # type: ignore[import-not-found]

from witchculttranslation.html_parsing.toc import parse_toc
from witchculttranslation.http_utils import get_response
from witchculttranslation.constants import ROOT, WITCHCULTTRANSLATION_TOC_URL
from witchculttranslation.interactors.download_arc import DownloadArcDTO, DownloadArc

logger = getLogger(__name__)


@click.command("download-rezero-arc")
@click.option("--output", help="Path for the book output", default=None, type=Path)
def download_rezero_arc(output: Path | None) -> None:
    logger.info("Download rezero arc: output=%s", output)

    toc_html = get_response(WITCHCULTTRANSLATION_TOC_URL).text
    toc_soup = bs4.BeautifulSoup(toc_html, (html_parser := "html.parser"))
    available_arcs = parse_toc(toc_soup)

    selected_arc_idx: int | None = questionary.select(
        "Choose an arc to download:",
        choices=[
            questionary.Choice(title=arc.name, value=idx)
            for idx, arc in enumerate(available_arcs)
        ],
    ).ask()

    if selected_arc_idx is None:
        click.echo("Operation cancelled.")
        return

    selected_arc = available_arcs[selected_arc_idx]

    total_chapters_to_download = sum(
        [len(phase.chapters) for phase in selected_arc.phases]
    )

    download_arc = DownloadArc(
        click.progressbar(length=total_chapters_to_download, label="Downloading"),
        html_parser,
    )
    result_path = output or ROOT / f"{selected_arc.name}.epub"
    result_path = download_arc(
        DownloadArcDTO(arc=selected_arc, result_path=result_path)
    )
    logger.info("Su")


if __name__ == "__main__":
    download_rezero_arc()
