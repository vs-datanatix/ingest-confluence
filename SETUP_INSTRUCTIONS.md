# Setup Instructions: Confluence → GitHub Standards Sync

This guide will help you configure the automated workflow that syncs development standards from Confluence to your GitHub repository.

## 🎯 Overview

The workflow will:
- ✅ Pull development standards from your Confluence page daily at midnight UTC
- ✅ Convert the Confluence page to Markdown format
- ✅ Store it in `.github/DEVELOPMENT_STANDARDS.md`
- ✅ Commit changes directly to the main branch (only if standards change)
- ✅ Protect the file so only you and the workflow can modify it

## 📋 Prerequisites

1. Confluence Cloud account with access to the standards page
2. GitHub repository with Actions enabled
3. Admin access to the repository (for branch protection rules)

---

## 🔧 Step 1: Create Confluence API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give it a name: `GitHub Standards Sync`
4. Copy the token (you won't see it again!)

---

## 🔐 Step 2: Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these two secrets:

### Secret 1: CONFLUENCE_EMAIL
- **Name**: `CONFLUENCE_EMAIL`
- **Value**: Your Atlassian account email (e.g., `your.email@company.com`)

### Secret 2: CONFLUENCE_API_TOKEN
- **Name**: `CONFLUENCE_API_TOKEN`
- **Value**: The API token you created in Step 1

---

## 🛡️ Step 3: Configure CODEOWNERS

1. Open `.github/CODEOWNERS` file
2. Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username
   ```
   /.github/DEVELOPMENT_STANDARDS.md @your-actual-username
   /.github/CODEOWNERS @your-actual-username
   /.github/workflows/sync-development-standards.yml @your-actual-username
   ```
3. Commit the change

---

## 🔒 Step 4: Set Up Branch Protection Rules

To ensure only you and the workflow can modify the standards file:

1. Go to **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Configure as follows:

### Branch name pattern
```
main
```

### Protection settings

✅ **Require a pull request before merging**
- ❌ Uncheck "Require approvals" (to allow direct commits from workflow)
  
✅ **Require status checks to pass before merging**
- Search and add: `sync-standards` (if you want to validate the workflow)

✅ **Require conversation resolution before merging**

✅ **Include administrators** (important!)

✅ **Restrict who can push to matching branches**
- Add: Your GitHub username
- Add: `github-actions[bot]` (allows the workflow to commit)

✅ **Allow force pushes**
- Specify who: Add your username only

✅ **Lock branch**
- ❌ Leave unchecked (would prevent all changes)

4. Click **Create** or **Save changes**

### Alternative: Rulesets (New GitHub Feature)

If your repository uses Rulesets instead of branch protection rules:

1. Go to **Settings** → **Rules** → **Rulesets**
2. Create a new ruleset for the `main` branch
3. Add bypass permissions for:
   - Your user account
   - GitHub Actions (`github-actions[bot]`)
4. Add restrictions for the protected files:
   - `.github/DEVELOPMENT_STANDARDS.md`
   - `.github/CODEOWNERS`
   - `.github/workflows/sync-development-standards.yml`

---

## 🚀 Step 5: Test the Workflow

### Manual Test
1. Go to **Actions** tab in your repository
2. Click on **Sync Development Standards from Confluence**
3. Click **Run workflow** → **Run workflow**
4. Wait for the workflow to complete
5. Check `.github/DEVELOPMENT_STANDARDS.md` to see the synced content

### Verify Protection
1. Try to edit `.github/DEVELOPMENT_STANDARDS.md` directly via GitHub UI
2. You should be able to commit (you're the owner)
3. Ask a team member to try editing it
4. They should be blocked (CODEOWNERS enforcement requires you to approve)

---

## 📅 Schedule

The workflow runs automatically:
- **Schedule**: Daily at 00:00 UTC (midnight)
- **Manual**: Can be triggered anytime from the Actions tab
- **Smart**: Only commits if changes are detected (won't spam your commit history)

---

## 🔍 Monitoring

### Check Workflow Status
- Go to **Actions** tab → **Sync Development Standards from Confluence**
- View run history and logs

### Notifications
- GitHub will send you email notifications if the workflow fails
- Check **Settings** → **Notifications** to customize

### Manual Sync
If you need to sync immediately (not waiting for midnight):
1. Go to **Actions** tab
2. Select the workflow
3. Click **Run workflow**

---

## 🛠️ Troubleshooting

### Workflow fails with "401 Unauthorized"
- Check that `CONFLUENCE_EMAIL` secret is correct
- Verify `CONFLUENCE_API_TOKEN` is valid and not expired
- Ensure your Atlassian account has access to the page

### Workflow fails with "403 Forbidden"
- Check if your Confluence page permissions allow API access
- Verify the page ID (196997) is correct
- Try accessing the page URL in your browser while logged out

### No changes detected but page was updated
- Check if the Confluence page was saved (not just previewed)
- Verify the workflow is fetching the correct page ID
- Check workflow logs for the fetched content

### Changes not committing
- Verify branch protection rules allow `github-actions[bot]` to push
- Check that the workflow has `contents: write` permission (already configured)
- Review the "Commit and push changes" step in workflow logs

### CODEOWNERS not blocking others
- Ensure branch protection rule "Require a pull request before merging" is enabled
- Check that CODEOWNERS file is in the correct location (`.github/CODEOWNERS`)
- Verify GitHub username in CODEOWNERS matches exactly (case-sensitive)

---

## 📝 File Structure

```
poc-gh-capabilities/
├── .github/
│   ├── workflows/
│   │   └── sync-development-standards.yml    # Main workflow
│   ├── CODEOWNERS                             # Access control
│   └── DEVELOPMENT_STANDARDS.md               # Auto-synced standards
├── SETUP_INSTRUCTIONS.md                      # This file
└── README.md
```

---

## 🎯 Next Steps

After setup is complete:

1. ✅ Test the workflow manually to verify it works
2. ✅ Update your Confluence page and wait for next sync (or trigger manually)
3. ✅ Create your PR validation workflow (separate task)
4. ✅ Reference `.github/DEVELOPMENT_STANDARDS.md` in your validation workflow
5. ✅ Add a link to the standards in your README or contributing guide

---

## 🔗 Useful Links

- [Confluence REST API Documentation](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

---

## 💡 Pro Tips

1. **Keep your API token secure**: Never commit it to the repository or share it
2. **Monitor the workflow**: Check it periodically to ensure it's running successfully
3. **Document changes**: Update the Confluence page with clear change logs
4. **Backup standards**: Consider keeping a backup of your standards elsewhere
5. **Version control**: Git history will track all changes to your standards over time

---

## 📞 Support

If you encounter issues:
1. Check the workflow logs in the Actions tab
2. Review this setup guide again
3. Verify all secrets and permissions are correctly configured
4. Check Confluence API status at [Atlassian Status](https://status.atlassian.com/)

---

**✨ Setup Complete!** Your development standards will now stay in sync automatically.
