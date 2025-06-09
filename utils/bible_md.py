import os
from textwrap import dedent
from inspect import cleandoc

from lib.bible_books import books

def create_markdown_files(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    cards = f"""\
<div class="grid cards" markdown>\n
- :fontawesome-solid-book-bible: __bible__\n
    ---\n
    Content\n
- :material-scale-balance: __scales__\n
    ---\n
    Content\n
</div>\n"""

    for idx, book in enumerate(books, start=1):
        number = f"{idx:02}"  # Zero-padded to 2 digits
        filename = f"{number}_{book.replace(' ', '_')}.md"
        filepath = os.path.join(output_dir, filename)

        content = f"""\
---
title: {number} {book}
tags: 
    - bible
---\n
## About\n
<div class="grid cards" markdown>\n
- :octicons-person-24: __Author__ author
- :material-calendar-edit: __Author Date__ date\n
</div>\n
## Memory verses\n\n
use md-bba\n
## Attitudes\n
What attitudes are we taught\n
{cards}
## Key Topics\n
{cards}
## Types\n
What types are seen as shadows of a truth.\n
{cards}
## Prophecies\n
{cards}
## References\n
- [search icons](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/)\n"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created {filepath}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate markdown files for Bible books.")
    parser.add_argument(
        "--outpath", "-o", type=str, required=True,
        help="Path to the output directory for the markdown files."
    )
    args = parser.parse_args()

    create_markdown_files(args.outpath)