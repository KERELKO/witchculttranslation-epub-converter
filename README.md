# witchculttranslation

CLI tools for downloading Re:Zero web novel content from Witch Cult Translations and exporting it to EPUB.

## What this project does

- Download a full arc interactively and save it as one EPUB.
- Download a single chapter by URL.
- Append single chapters into an existing EPUB.
- Automatically set metadata and cover images when available.

## Requirements

- Python 3.14+
- `uv` installed: https://docs.astral.sh/uv/

## Installation

From the project root:

```bash
uv sync
```

This installs dependencies and registers the CLI entrypoints.

## Quick Start

### 1) Download a full arc (interactive)

```bash
uv run download-rezero-arc
```

You will get an interactive prompt like:

```text
Built witchculttranslation @ file:///home/kerelko/programming/witchculttranslation
Uninstalled 1 package in 0.92ms
Installed 1 package in 2ms
? Choose an arc to download: (Use arrow keys)
 » Arc 1 – A Tumultuous First Day
   Arc 2 – The Chaotic Week
   Arc 3 – Return to the Royal Capital
   Arc 4 – Everlasting Contract
   Arc 5 – Stars What Make History
   Arc 6 – Hall of Memories
   Arc 7 – The Land of Wolves
   Arc 8 – Vincent Vollachia
   Arc 9 – Light of a Nameless Star
   Arc 10 – The Land of the Lion Kings
```

After you select an arc, chapters are downloaded with a progress bar, and an EPUB is written to the repository root by default.

### 2) Download a single chapter by URL

```bash
uv run download-rezero-chapter \
  --url "https://witchculttranslation.com/..."
```

If you do not pass `--book`, this creates a new book named:

- `Re:Zero − Starting Life in Another World: Web novel.epub`

in the repository root.

## CLI Reference

### `download-rezero-arc`

Downloads one selected arc into an EPUB.

```bash
uv run download-rezero-arc [--output PATH]
```

Options:

- `--output PATH`: output EPUB path. If omitted, output goes to repository root using the selected arc name.

Examples:

```bash
# Save to default path (repo root)
uv run download-rezero-arc

# Save to a custom file
uv run download-rezero-arc --output output/arc-7.epub
```

### `download-rezero-chapter`

Downloads one chapter URL and writes it into a new or existing EPUB.

```bash
uv run download-rezero-chapter --url URL [--book PATH] [--output PATH]
```

Options:

- `--url URL`: chapter URL on witchculttranslation.com (required).
- `--book PATH`: existing EPUB to append to.
- `--output PATH`: output path for a newly created book when `--book` is not provided.

Examples:

```bash
# Create a new EPUB with one chapter
uv run download-rezero-chapter \
  --url "https://witchculttranslation.com/..." \
  --output output/first-chapter.epub

# Append a chapter to an existing EPUB
uv run download-rezero-chapter \
  --url "https://witchculttranslation.com/..." \
  --book output/arc-7.epub
```

## Practical workflows

### Build an arc EPUB and store it in output/

```bash
uv run download-rezero-arc --output output/arc-7-the-land-of-wolves.epub
```

### Keep collecting chapters into one personal volume

```bash
uv run download-rezero-chapter \
  --url "https://witchculttranslation.com/..." \
  --book output/my-rezero-volume.epub
```

### Use default naming and location (fastest)

```bash
uv run download-rezero-arc
uv run download-rezero-chapter --url "https://witchculttranslation.com/..."
```

## Error notes

- Empty `--url` is rejected by the CLI.
- Invalid chapter URLs return a clear argument error.
- If you cancel arc selection, the command exits without writing files.

## Development

Install dev dependencies:

```bash
uv sync --group dev
```

Run a local command directly from source:

```bash
uv run download-rezero-arc
```
