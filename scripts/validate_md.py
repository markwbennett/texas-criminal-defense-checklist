#!/usr/bin/env python3
"""Structure validator for CriminalDefenseChecklist.md. Run before committing
template edits; CI runs it on every pull request.

Checks: the Markdown converts cleanly to the internal outline; indentation
never jumps more than one level; form fences are balanced; the file has
sections and items. With a reference tab-indented file as a second argument
(the retired txt), it additionally verifies a lossless round trip."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from convert_checklist import md_to_tab_text

def stream(tab_text):
    items = []
    for line in tab_text.split("\n"):
        if not line.strip():
            continue
        if line.strip().startswith("# Tab for increasing"):
            continue
        if line.strip().lower() == "#end":
            continue
        depth = len(line) - len(line.lstrip("\t"))
        items.append((depth, line.strip()))
    return items

def structural(md_path):
    md = Path(md_path).read_text()
    errs = []
    fence_open = 0
    for n, line in enumerate(md.split("\n"), 1):
        s = line.strip()
        if s.startswith("```form"):
            if fence_open:
                errs.append(f"line {n}: nested ```form fence")
            fence_open = 1
        elif s == "```" and fence_open:
            fence_open = 0
    if fence_open:
        errs.append("unclosed ```form fence at end of file")

    tab = md_to_tab_text(md)
    prev = 0
    in_form = False
    sections = items = 0
    for n, line in enumerate(tab.split("\n"), 1):
        s = line.strip()
        if not s:
            continue
        if s.upper() == "#FORM":
            in_form = True
            prev = len(line) - len(line.lstrip("\t"))
            continue
        if s.upper() == "#FORMEND":
            in_form = False
            continue
        if in_form or s.startswith("#"):
            continue
        depth = len(line) - len(line.lstrip("\t"))
        if depth > prev + 1:
            errs.append(f"outline line {n}: indentation jumps {prev} -> {depth}: {s[:60]}")
        prev = depth
        if depth == 0:
            sections += 1
        else:
            items += 1
    if sections < 2:
        errs.append(f"only {sections} top-level sections found")
    if items < 50:
        errs.append(f"only {items} checklist items found")
    return errs, sections, items

def main(argv):
    md = argv[1] if len(argv) > 1 else "CriminalDefenseChecklist.md"
    ref = argv[2] if len(argv) > 2 else None
    errs, sections, items = structural(md)
    if ref and Path(ref).exists():
        md_stream = stream(md_to_tab_text(Path(md).read_text()))
        ref_stream = stream(Path(ref).read_text())
        if md_stream != ref_stream:
            for i, (a, b) in enumerate(zip(md_stream, ref_stream)):
                if a != b:
                    errs.append(f"round-trip divergence at outline line {i}: md={a} ref={b}")
                    break
            else:
                errs.append(f"round-trip length mismatch: md={len(md_stream)} ref={len(ref_stream)}")
        else:
            print(f"round-trip OK: {len(md_stream)} outline lines identical")
    if errs:
        for e in errs:
            print("FAIL:", e)
        return 1
    print(f"structure OK: {sections} sections, {items} items, fences balanced")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
