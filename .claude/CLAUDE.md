# Project Instructions for Claude

## GitHub Synchronization

**BEFORE starting any edits:**
```bash
# Check if this is a git repository
git status

# Pull latest changes from GitHub
git pull origin main
```

**BEFORE exiting or ending the session:**
```bash
# Commit all changes
git add .
git commit -m "Your commit message"

# Push changes to GitHub
git push origin main
```

## Important Notes
- Always sync with GitHub before making any changes
- Always push changes to GitHub before ending the session
- Check `git remote -v` if you're unsure about the remote configuration
