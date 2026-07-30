# poc-gh-capabilities

This repo is to showcase capabilities of GitHub

## 🔄 Automated Development Standards Sync

This repository includes an automated workflow that synchronizes development standards from Confluence to GitHub:

- **Source**: [Confluence Development Standards](https://datanatix.atlassian.net/wiki/spaces/PS/pages/196997/Development+Standards)
- **Target**: [`.github/DEVELOPMENT_STANDARDS.md`](.github/DEVELOPMENT_STANDARDS.md)
- **Schedule**: Daily at midnight UTC
- **Access Control**: Protected via CODEOWNERS and branch protection

### Quick Start

1. **Setup Required**: Follow [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) to configure the workflow
2. **View Standards**: Check [`.github/DEVELOPMENT_STANDARDS.md`](.github/DEVELOPMENT_STANDARDS.md) for current standards
3. **Trigger Manually**: Go to Actions → "Sync Development Standards" → Run workflow

### How It Works

1. The workflow fetches the Confluence page via REST API
2. Converts HTML content to Markdown format
3. Compares with the existing file in the repository
4. Commits changes only if standards have been updated
5. Ensures only authorized users and the workflow can modify the standards

### Features

✅ Automatic daily synchronization  
✅ Manual trigger available  
✅ Change detection (no unnecessary commits)  
✅ Protected file access (CODEOWNERS)  
✅ Full audit trail in Git history  
✅ Clear source attribution with links back to Confluence

---

For detailed setup instructions, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
