# Texas Criminal-Defense Checklist

A comprehensive, hierarchical checklist for criminal-defense practice in Texas, published by the **Institute for Advanced Criminal Law Studies (IACLS)**. It covers the life of a case from the first client meeting through trial, appeal, and record clearing, with error-preservation pages for each phase of trial and offense-specific sections (currently DWI).

The checklist lives in one Markdown file, [`CriminalDefenseChecklist.md`](CriminalDefenseChecklist.md), which GitHub renders as nested task lists — browse it right here, or use it through the web app or the PDF.

## Three ways to use it

1. **Web app** — open [`checklist-app.html`](checklist-app.html) in any browser. Create a checklist per client, check items off, and export encrypted backups. Everything stays in your browser; nothing is sent anywhere. See [`CHECKLIST_APP_README.md`](CHECKLIST_APP_README.md).
2. **PDF** — download [`CriminalDefenseChecklist.pdf`](CriminalDefenseChecklist.pdf), rebuilt automatically whenever the checklist changes. One page per sublist, with page-number cross-references and stacked breadcrumb navigation.
3. **On GitHub** — read [`CriminalDefenseChecklist.md`](CriminalDefenseChecklist.md) directly; the section list in the header is a table of contents, and every item renders as a checkbox.

## The template format

`CriminalDefenseChecklist.md` is ordinary Markdown with a few conventions:

| Convention | Meaning |
|---|---|
| `## Heading` | Top-level section (a phase of the case) |
| `- [ ] Item`, nested two spaces per level | A checklist item |
| Trailing `_` | Fill-in field (renders as a blank line in print) |
| Trailing `*` | Keep this item's sublist on the same printed page |
| `- *Note:* text` | Explanatory note, displayed but not checkable |
| ```` ```form … ``` ```` fenced block | A client-intake form, kept together in print |
| `<!-- comment -->` | Ignored by all the tools |

The blockquote at the top of the file is the currency line: the date the checklist was last substantively reviewed against Texas law. Statutes and article numbers age silently — check the date before relying on any item.

## Editing and contributing

Edit `CriminalDefenseChecklist.md` in any text editor or directly on GitHub, then open a pull request. Two checks run on every PR:

- `scripts/validate_md.py` verifies the file's structure (indentation continuity, balanced form fences).
- The PDF workflow rebuilds `CriminalDefenseChecklist.pdf` after merge, so the published PDF always matches the Markdown.

The checklist is designed to be customized: fork it and adjust the wording, contacts, and offense sections to your jurisdiction and practice. The Harris County contact details in the discovery section are local and age quickly — verify before relying on them.

## Repository contents

| File | Purpose |
|---|---|
| `CriminalDefenseChecklist.md` | The checklist (canonical source) |
| `CriminalDefenseChecklist.pdf` | Print edition, rebuilt automatically from the Markdown |
| `checklist-app.html` | Interactive web app (self-contained, offline-capable) |
| `checklist-app-single-page.html` | Legacy single-page variant of the app |
| `convert_checklist.py` | PDF generator (`python convert_checklist.py CriminalDefenseChecklist.md`; needs `weasyprint`, `markdown`, `beautifulsoup4`) |
| `scripts/validate_md.py` | Structure validator; run before committing template edits |
| `scripts/txt_to_md.py` | Converter from the retired tab-indented format |
| `arial_px_pt_ratios.csv` | Character-width data used by the PDF generator |
| `CHECKLIST_APP_README.md` | User guide for the web app |

## Credits

Developed by the **Institute for Advanced Criminal Law Studies**, [IACLS.org](https://iacls.org).

## License

See [`LICENSE`](LICENSE).
