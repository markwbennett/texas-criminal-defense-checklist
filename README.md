# Texas Criminal Defense Checklist

A comprehensive, hierarchical checklist for criminal defense practice in Texas, developed by the **Institute for Advanced Criminal Law Studies (IACLS)**.

## Overview

This project provides a complete criminal defense workflow checklist covering everything from initial client meeting through appeal and record clearing. The checklist includes general criminal defense procedures plus offense-specific sections (currently DWI cases, with room for expansion).

## Components

### 1. Interactive Web Application (`checklist-app.html`)

A self-contained, browser-based checklist manager with:

- **Per-client instances** - Create unlimited client checklists with independent state tracking
- **Smart checkboxes** - Parent items auto-complete when all children are checked
- **Template-driven** - Loads from `CriminalDefenseChecklist.txt` (user-editable)
- **Progress tracking** - Visual indicators show completion percentage
- **Data persistence** - Auto-saves to browser localStorage with export/import to JSON
- **Printable forms** - Generate fillable PDF forms for questionnaires and intake documents
- **Collapsible sections** - Clean, organized interface with expand/collapse
- **Search functionality** - Quickly find checklist items
- **No installation required** - Works in any modern browser, offline-capable
- **IACLS branding** - Professional appearance with organization logo and attribution

**Quick Start:**
1. Open `checklist-app.html` in your browser
2. Template auto-loads (or click "Load Template" if needed)
3. Click "New Client" to create a checklist
4. Check off items as you complete them

See `CHECKLIST_APP_README.md` (or `.pdf`) for detailed documentation.

### 2. Master Checklist Template (`CriminalDefenseChecklist.txt`)

The source template file with hierarchical structure:

**Format:**
- Tabs indicate outline levels (more tabs = deeper nesting)
- `_` at line end = fillable field
- `#FORM` / `#FORMEND` = form sections
- `#Note:` = explanatory notes
- `#End` = marks end of template
- `#` alone = comment (not displayed)

**Structure:**
- Prospective Client Meeting
- Client Background Investigation
- Open File
- Stabilize Case
- Discovery and Investigation (with subsections)
- Mitigation
- Review Discovery
- Scientific and Technical Issues
- Motions Practice
- Build a Team
- Case Reassessment and Negotiation
- Plea Offers / Guilty Plea
- Trial (Preparation and Execution)
- Appeal
- Close File / Clear Client's Record
- Prepare for Disaster
- **Offense-Specific Checklists**
  - DWI Cases (Initial Meeting, Pretrial, ALR Hearing, Occupational License, ALR Forms)
  - *(Room for additional offense types)*

All sections maintain ≤20 items per hierarchy level for usability.

**Editing the Template:**
Moderately technical users can edit `CriminalDefenseChecklist.txt` in any text editor to modify the checklist structure. The web app will parse changes when the template is reloaded.

### 3. PDF Generator (`convert_checklist.py`)

Optional Python script to generate printable PDF versions of the checklist with:
- Hierarchical navigation with breadcrumb links
- Page breaks between sections
- Special formatting for forms
- Proper underlines for fillable fields

**Requirements:** Python 3 with `weasyprint`, `markdown`, `beautifulsoup4`

**Usage:**
```bash
python convert_checklist.py CriminalDefenseChecklist.txt
```

## Files

| File | Purpose |
|------|---------|
| `checklist-app.html` | Interactive web application (self-contained) |
| `CriminalDefenseChecklist.txt` | Master checklist template (user-editable) |
| `CHECKLIST_APP_README.md` | User guide for web application |
| `CHECKLIST_APP_README.pdf` | Printable user guide |
| `convert_checklist.py` | PDF generator script (optional) |
| `arial_px_pt_ratios.csv` | Character width data for PDF generation |

## Credits

Developed by the **Institute for Advanced Criminal Law Studies**
[IACLS.org](https://iacls.org)

## License

See `LICENSE` file for details.

## Contributing

This checklist is designed to be customized for your practice. Edit `CriminalDefenseChecklist.txt` to add, remove, or modify sections as needed.

For issues or suggestions, please open an issue on GitHub.
