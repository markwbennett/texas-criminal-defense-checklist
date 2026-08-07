#!/usr/bin/env python3
"""Round-trip validator: CriminalDefenseChecklist.md must reconstruct the
same outline as the reference tab-indented text. Used as the PR check."""
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
            continue  # old txt format doc, intentionally not carried to MD
        if line.strip().lower() == "#end":
            continue  # txt terminator; the MD format has none
        depth = len(line) - len(line.lstrip("\t"))
        items.append((depth, line.strip()))
    return items

def main(md_path, ref_path):
    md_stream = stream(md_to_tab_text(Path(md_path).read_text()))
    ref_stream = stream(Path(ref_path).read_text())
    if md_stream == ref_stream:
        print(f"round-trip OK: {len(md_stream)} outline lines identical")
        return 0
    for i, (a, b) in enumerate(zip(md_stream, ref_stream)):
        if a != b:
            print(f"first divergence at outline line {i}:\n  md : {a}\n  ref: {b}")
            break
    else:
        i = min(len(md_stream), len(ref_stream))
        print(f"length mismatch at line {i}: md={len(md_stream)} ref={len(ref_stream)}")
        for extra in (md_stream[i:i+3] or ref_stream[i:i+3]):
            print("  ", extra)
    return 1

if __name__ == "__main__":
    md = sys.argv[1] if len(sys.argv) > 1 else "CriminalDefenseChecklist.md"
    ref = sys.argv[2] if len(sys.argv) > 2 else "CriminalDefenseChecklist.txt"
    sys.exit(main(md, ref))
