# Masters Abroad Tracker
1. Create a GitHub repo, upload everything in this folder (keep `docs/`, `scripts/`, `.github/`).
2. Settings > Pages > Source: `main` branch, folder `/docs`. Your site goes live at https://USERNAME.github.io/REPO/
3. (Optional, for auto-extraction of deadlines/tests) Settings > Secrets and variables > Actions > New secret `ANTHROPIC_API_KEY`.
4. Actions tab > "daily-update" > Run workflow once to test. It then runs every day at 02:00 UTC.
Without the key, it only detects official-page changes (shows "page changed"). Deadlines still count down automatically in the browser.
Add universities by appending to `docs/data.json` (same fields as existing entries) - the checker picks them up next run.
