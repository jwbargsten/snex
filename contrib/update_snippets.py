import snex
from snex.core import Snippet
import pathspec
import re
import sys
import os.path


snippets = {}
for snippet_spec in snex.visit(".", "snex.conf.yaml"):
    snippet = snippet_spec["snippet"]
    sid = f"{snippet.origin}::{snippet.name}"
    snippets[sid] = snippet_spec["rendered"]

start_marker = r"^<!-- include (.*::.*) -->$"
end_marker = r"^<!-- endinclude -->$"

print(list(snippets.keys()), file=sys.stderr)

spec = pathspec.PathSpec.from_lines("gitwildmatch", ["*.md", "!/snippets/"])
root = "devdocs/"
matches = spec.match_tree(root)


def transform_file(f, snippets: dict[str, Snippet]):
    lines = []
    had_snippet = False
    with open(f) as fd:
        in_section = False
        for line in fd:
            if in_section and re.search(end_marker, line):
                in_section = False
                lines.append(line)
                continue

            if m := re.search(start_marker, line):
                snippet_id = str(m.group(1)).strip()
                in_section = True
                if snippet_id in snippets:
                    had_snippet = True
                    snippet = snippets[snippet_id]
                    lines.append(line)
                    lines.append(snippet)
                continue
            if not in_section:
                lines.append(line)
    return "".join(lines), had_snippet


for filematch in matches:
    md_file = os.path.join(root, filematch)
    data, had_snippet = transform_file(md_file, snippets)
    if had_snippet:
        with open(md_file, "w") as fd:
            fd.write(data)
