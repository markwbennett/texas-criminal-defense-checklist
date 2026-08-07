#!/usr/bin/env python3
"""One-time (and reusable) converter: tab-indented checklist txt -> Markdown.

Mapping (canonical, shared with the md shims in convert_checklist.py and
checklist-app.html):
  txt depth 0            <-> "## " heading
  txt depth k>=1         <-> task-list item indented (k-1)*2 spaces
  #Note: X               <-> "- *Note:* X" list entry at the same indent
  other "#..." comments  <-> "<!-- #... -->" at the same indent
  #FORM ... #FORMEND     <-> fenced block ```form at the parent item's child
                             indent; inner lines keep depth relative to the
                             form as literal tabs
  # CURRENCY: X (header) <-> "> **Currency:** X" blockquote under the title
Trailing _ (fill-in) and * (keep-with-sublist) flags ride along verbatim.
"""
import sys
from pathlib import Path

def convert(txt: str) -> str:
    lines = txt.split("\n")
    out = [
        "# Texas Criminal-Defense Checklist",
        "",
    ]
    fmt_doc = (
        "<!-- FORMAT: '## ' headings are top-level sections. '- [ ] ' items nest at "
        "two spaces per level. A trailing _ marks a fill-in field; a trailing * keeps "
        "the sublist on the same page. '- *Note:*' entries are display notes. "
        "```form fenced blocks are intake forms (inner tabs are relative depth). "
        "HTML comments are ignored by the tools. -->"
    )
    i = 0
    in_form = False
    form_indent = ""
    body = []
    currency = None
    while i < len(lines):
        raw = lines[i].rstrip("\n")
        stripped = raw.strip()
        depth = len(raw) - len(raw.lstrip("\t"))
        i += 1

        if stripped.lower() == "#end":
            break

        if in_form:
            if stripped.upper() == "#FORMEND":
                body.append(form_indent + "```")
                in_form = False
                continue
            # relative depth inside the form: strip (form_depth+1) tabs
            rel = raw
            for _ in range(form_base):
                if rel.startswith("\t"):
                    rel = rel[1:]
            body.append(form_indent + rel if rel.strip() else form_indent.rstrip())
            continue

        if stripped.upper() == "#FORM":
            # fence belongs to the preceding item (depth-1 item's child column)
            form_indent = " " * ((depth - 1) * 2 + 2)
            form_base = depth + 1
            body.append(form_indent + "```form")
            in_form = True
            continue

        if not stripped:
            body.append("")
            continue

        if stripped.startswith("#Note:"):
            note = stripped[len("#Note:"):].strip()
            body.append(" " * ((depth - 1) * 2) + f"- *Note:* {note}")
            continue

        if stripped.startswith("#"):
            if stripped.startswith("# CURRENCY:") and depth == 0 and currency is None:
                currency = stripped[len("# CURRENCY:"):].strip()
                continue
            if depth == 0 and stripped.startswith("# Tab for increasing"):
                continue  # old format doc, replaced by the MD format comment
            body.append(" " * (max(depth - 1, 0) * 2) + f"<!-- {stripped} -->")
            continue

        if depth == 0:
            body.append("")
            body.append(f"## {stripped}")
            continue

        body.append(" " * ((depth - 1) * 2) + f"- [ ] {stripped}")

    if currency:
        out.append(f"> **Currency:** {currency}")
        out.append("")
    out.append(fmt_doc)
    out.append("")
    # collapse runs of blank lines
    collapsed = []
    for line in body:
        if line == "" and collapsed and collapsed[-1] == "":
            continue
        collapsed.append(line)
    out.extend(collapsed)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "CriminalDefenseChecklist.txt")
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else src.with_suffix(".md"))
    dst.write_text(convert(src.read_text()))
    print(f"wrote {dst}")
