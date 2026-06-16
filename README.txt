WORLD CUP 2026 TOURNAMENT HUB

FILES
- index.html: display page
- data.json: standings and upcoming matches
- update_fifa.py: server-side FIFA updater
- .github/workflows/update-fifa.yml: runs every five minutes

GITHUB SETUP
1. Upload every file and folder to the root of your GitHub repository.
2. Open Settings > Pages.
3. Choose Deploy from a branch and select the main branch / root folder.
4. Open the Actions tab and enable workflows if GitHub asks.
5. Run “Update FIFA tournament data” once manually.

HOW IT WORKS
- GitHub Actions opens FIFA’s official scores/fixtures page in a real headless browser.
- It captures structured match data returned by FIFA’s site.
- It recalculates group standings and writes the next eight fixtures to data.json.
- The webpage checks data.json once per minute without reloading the full screen.
- GitHub Actions schedules cannot run more often than approximately every five minutes.

RELIABILITY
FIFA does not publish a documented, browser-friendly public JSON API for this page.
The updater therefore reads FIFA’s official page server-side. If FIFA changes its site
format, the script preserves the last-known-good data rather than clearing the display.
