import re
from pathlib import Path

HTML_INDENT = "    "


def format_html(filepath: Path) -> str:
    """Reads the content of an HTML Bookmarks file and reformats it to simplify tree traversal
    after the contents are parsed by BeautifulSoup.
    The content is reformatted as follows;
    - The main "<H1>" tag is converted to "<H3>" and acts as the root folder
    - All "<DT>" tags are removed.
    - "<H3>" acts as folders and list containers instead of "<DL>".
    - All "<H3>" and "<A>" tag's inner text are added as a "title"
    attribute within the html element.

    filepath: str
        absolute path to bookmarks html file.
    """
    with filepath.open("r", encoding="utf-8") as input_file:
        # regex to select an entire H1/H3/A HTML element
        element = re.compile(r"(<(H1|H3|A))(.*?(?=>))>(.*)(<\/\2>)\n")

        def _format(line: str) -> str:
            line = element.sub(r'\1\3 TITLE="\4">\5', line)
            return (
                line.replace("<DL><p>", "")
                .replace("<DT>", "")
                .replace("<H1", "<H3")
                .replace("</H1>", "")
                .replace("</H3>", "")
                .replace("</DL><p>\n", "</H3>")
                .replace("</DL>", "</H3>")
                .replace("\n", "")
                .strip()
            )

        lines = [_format(line) for line in input_file]
        return "".join(lines)


def indent_html(html: str) -> str:
    """Adds indentation to HTML Bookmarks file."""
    output = ""
    depth = 0
    for line in html.splitlines():
        if line.startswith("</DL>"):
            depth -= 1

        output += f"{depth*HTML_INDENT}{line}\n"

        if line.startswith("<DL><p>"):
            depth += 1

    return output
