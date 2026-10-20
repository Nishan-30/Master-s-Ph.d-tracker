# Masters abroad tracker
Folder layout: docs/index.html, docs/data.json, scripts/update.py, .github/workflows/update.yml
Pages: Settings > Pages > Deploy from branch > main > /docs.
Actions: runs daily (02:00 UTC). No API key needed. It fetches each official page, flags changes, and fills a blank deadline or test score only when the page text states it clearly. Those values are labelled "Auto-detected - verify".
Limit: many links are department home pages, so the checker often finds nothing there. Replace a link in docs/data.json with the exact admissions page and the checker will start reading it.
