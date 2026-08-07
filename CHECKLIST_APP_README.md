# Criminal-Defense Checklist Web Application

## Quick Start

1. **Open `checklist-app.html` in your web browser** (double-click the file)
2. The template loads automatically from `CriminalDefenseChecklist.md` (or click **"Load Template"** and select it)
3. **Click "New Client"** to create your first checklist
4. Start checking off items!

## Features

### ✓ Template-Driven
- The checklist structure comes from `CriminalDefenseChecklist.md`
- Edit the Markdown file to modify the template (add/remove items)
- Reload the template in the app to see changes; existing clients keep the template they were created with

### ✓ Per-Client Instances
- Create unlimited client checklists
- Each client has independent state
- Progress tracked per client

### ✓ Smart Checkboxes
- Parent items auto-complete when all children are checked
- Progress indicators show completion percentage
- Visual feedback for completed items

### ✓ Data Management
- Auto-saves to browser localStorage
- **Export All** - Backup all clients in one file (recommended weekly)
- **Import All** - Restore all clients from backup
- **Optional Password Encryption** - Encrypt backups with AES-256
- Export or import individual client data as JSON
- Delete/archive old cases

### ✓ Search & Navigate
- Search box to filter items
- Collapsible sections (click ▼ to collapse)
- Paginated and single-page view modes

### ✓ Print Support
- Print-friendly formatting for checklists
- **Printable Forms** - Click "Print Form" on any form section to generate a fillable page: underscored fields become fillable lines, client info is pre-filled, and the browser's print dialog saves it as PDF

## How to Modify the Template

The template file (`CriminalDefenseChecklist.md`) is ordinary Markdown:

### Format Rules
- **`## Heading`** = a top-level section
- **`- [ ] Item`** = a checklist item; nest deeper levels by indenting two more spaces
- **`_` at end of line** = fillable field (e.g., `- [ ] Phone_`)
- **`*` at end of line** = keep this item's sublist on the same printed page
- **`- *Note:* text`** = explanatory note (displayed, but no checkbox)
- **```` ```form … ``` ````** fenced block = an intake form, kept together on one page
- **`<!-- comment -->`** = ignored entirely

### Example
```markdown
## Main Section
- [ ] Subsection
- [ ] Another Subsection
  - [ ] Detail item
  - [ ] Name_
  - *Note:* This is a helpful note
    ```form
    Form content here
    Line 1_
    Line 2_
    ```
```

### To Edit
1. Open `CriminalDefenseChecklist.md` in any text editor (or edit it on GitHub)
2. Make your changes and save
3. Run `python3 scripts/validate_md.py` to confirm the structure is sound
4. In the web app, click "Load Template" again
5. New clients will use the updated template

## Data Storage

### Where is data stored?
- **Browser localStorage** (automatic, no setup needed)
- **Your computer only** (not sent anywhere)
- Data persists between sessions
- Each browser keeps separate storage; use Export/Import to move between browsers

### ⚠️ IMPORTANT: Backup Your Data Regularly

Browser localStorage can be cleared by cache clearing, browser updates or crashes, switching browsers, or computer issues.

**Option 1: Export All (recommended)**
1. Click **"📦 Export All"** in the header
2. Save the backup file (`all_clients_backup_YYYY-MM-DD.json`)
3. Store it somewhere safe (cloud storage, external drive)
4. Repeat weekly or after significant updates

**Option 2: Export individual clients** with the "Export" button on each client card.

**To restore:** "📂 Import All" replaces all current data from a full backup; "📥 Import Client" adds one client from an individual file.

### Password Encryption (Optional)

When exporting, the app offers to encrypt the backup:

- AES-256-GCM encryption with PBKDF2 key derivation (100,000 iterations), random salt and IV per backup
- Minimum 8-character password; the filename gains an `_ENCRYPTED` marker
- Importing an encrypted file prompts for the password automatically

**⚠️ CRITICAL: There is no password recovery. A lost password means an unrecoverable backup.**

Use encryption whenever a backup lands in cloud storage, email, or any place an unauthorized person might reach it.

## Troubleshooting

### "Template not loading"
- Make sure you selected `CriminalDefenseChecklist.md` (the app also still reads the old tab-indented `.txt` format)
- Open the file in a text editor to verify it is readable
- Run `python3 scripts/validate_md.py` to check for structural problems

### "My clients disappeared"
- Check that you are using the same browser
- Import from your backup `.json` files
- A cleared browser cache deletes localStorage — keep backups

### "Items won't check"
- Refresh the page
- Check the browser console for errors (F12)
- Export and re-import the client

## Tips

- **Keyboard shortcut:** Ctrl/Cmd + S saves the current checklist
- **Collapse sections** you are not working on
- **Use Search** to find specific items quickly
- **Export regularly** ("Export All" weekly)
- **Print to PDF** for permanent records
- **Clear Storage** when using shared computers
- **Use encryption** for backups stored in cloud services

## System Requirements

- Any modern browser (Chrome, Firefox, Safari, Edge) on any platform
- Works offline; no installation, no server

## Privacy

- All data stays in your browser
- Nothing is sent to any server
- No tracking or analytics
