# Criminal Defense Checklist Web Application

## Quick Start

1. **Open `checklist-app.html` in your web browser** (double-click the file)
2. **Click "Load Template"** and select `CriminalDefenseChecklist.txt`
3. **Click "New Client"** to create your first checklist
4. Start checking off items!

## Features

### ✓ Template-Driven
- The checklist structure comes from `CriminalDefenseChecklist.txt`
- Edit the `.txt` file to modify the template (add/remove items)
- Reload the template in the app to see changes

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
- **Optional Password Encryption** - Encrypt backups with AES-256 for security
- Export individual client data to JSON file
- Import individual client data from JSON file
- Delete/archive old cases

### ✓ Search & Navigate
- Search box to filter items
- Collapsible sections (click ▼ to collapse)
- Clean, organized interface

### ✓ Print Support
- Print-friendly formatting for checklists
- **Printable Forms** - Click "Print Form" button on any #FORM section to generate a fillable PDF
  - Opens in new window with client info pre-filled
  - Underscored fields become fillable lines
  - Save as PDF using browser's print dialog
  - IACLS branding included

## How to Modify the Template

The template file (`CriminalDefenseChecklist.txt`) uses a simple format:

### Format Rules:
- **Tabs** = hierarchy (more tabs = deeper nesting)
- **_** at end of line = fillable field (e.g., `Phone_`)
- **#FORM** / **#FORMEND** = form sections (kept together)
- **#Note:** = explanatory notes (displayed in italics)
- **#End** = stop processing (everything after ignored)
- **#** alone = comment (not displayed)

### Example:
```
Main Section
	Subsection
	Another Subsection
		Detail item
		Name_
		#Note: This is a helpful note
		#FORM
			Form content here
			Line 1
			Line 2
		#FORMEND
```

### To Edit:
1. Open `CriminalDefenseChecklist.txt` in any text editor
2. Make your changes (add/remove items, change text)
3. Save the file
4. In the web app, click "Load Template" again
5. New clients will use the updated template

## Data Storage

### Where is data stored?
- **Browser localStorage** (automatic, no setup needed)
- **Your computer only** (not sent anywhere)
- Data persists between sessions

### Data Location by Browser:
- Each browser has separate storage
- Chrome, Firefox, Safari = different storage
- Use Export/Import to move between browsers

### ⚠️ IMPORTANT: Backup Your Data Regularly

**Browser localStorage can be cleared by:**
- Clearing browser cache/cookies
- Browser updates or crashes
- Switching browsers
- Computer issues

**To protect your data:**

**Option 1: Export All (Recommended - Easiest)**
1. Click **"📦 Export All"** button in the header
2. Save the backup file (named `all_clients_backup_YYYY-MM-DD.json`)
3. Store in a safe location (cloud storage, external drive)
4. Repeat weekly or after significant updates

**Option 2: Export Individual Clients**
1. Click "Export" on each client card
2. Save individual `.json` files
3. Useful for sharing specific cases or selective backups

**To restore:**
- **Restore all clients:** Click "📂 Import All" and select your backup file (replaces all current data)
- **Restore one client:** Click "📥 Import Client" and select an individual `.json` file (adds to existing clients)

### Password Encryption (Optional)

When exporting, you'll be asked if you want to encrypt the backup:

**Encrypting backups:**
1. Click "Export" or "Export All"
2. Choose "OK" when asked about encryption
3. Enter a strong password (minimum 8 characters)
4. Confirm password
5. File saved with "_ENCRYPTED" in filename

**Security features:**
- AES-256-GCM encryption (military-grade)
- PBKDF2 key derivation (100,000 iterations)
- Random salt and IV per backup
- No password recovery possible

**⚠️ CRITICAL: If you lose the password, the backup is permanently unrecoverable!**

**When to use encryption:**
- Storing backups in cloud storage (Dropbox, Google Drive)
- Emailing backups to yourself
- Sharing backup files with others
- Any situation where file might be accessed by unauthorized persons

**Importing encrypted backups:**
1. Select the encrypted file
2. App automatically detects encryption
3. Enter your password
4. Data decrypted and restored

**Unencrypted backups:**
- Choose "Cancel" when asked about encryption
- Simpler, no password to remember
- Only use if storing backups in secure location

## Troubleshooting

### "Template not loading"
- Make sure you selected the correct `.txt` file
- Check that the file is not corrupted
- Try opening the `.txt` file in a text editor to verify it's readable

### "My clients disappeared"
- Check if you're using the same browser
- Try importing from your backup `.json` files
- Clear browser cache might have deleted localStorage (always keep backups!)

### "Items won't check"
- Try refreshing the page
- Check browser console for errors (F12)
- Try exporting and re-importing the client

## Tips

- **Keyboard Shortcut:** Ctrl/Cmd + S saves the current checklist
- **Collapse sections** you're not working on to reduce clutter
- **Use Search** to quickly find specific items
- **Export regularly** as backup (use "Export All" weekly)
- **Print to PDF** for permanent records or court submissions
- **Clear Storage** when using shared/public computers for security
- **Use encryption** when storing backups in cloud services

## System Requirements

- Any modern web browser (Chrome, Firefox, Safari, Edge)
- Works on Windows, Mac, Linux, tablets, phones
- No internet connection required (works offline)
- No installation needed

## Privacy

- All data stored locally in your browser
- Nothing sent to any server
- No tracking or analytics
- Completely private and secure
