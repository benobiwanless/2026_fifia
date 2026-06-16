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


LAYOUT UPDATE
- Standings now use a 3-column x 4-row grid on the left.
- Right side shows today's matches only.
- Below the schedule is a rotating leader-stats panel for Goals, Assists, Yellow Cards, and Red Cards.
- The page auto-refreshes data.json every minute.


FULL STANDINGS + LEADER PAGES
- Left side shows two full group tables per page.
- Each table includes MP, W, D, L, GF, GA, GD, PTS, and Last 5.
- Standings pages advance every 10 seconds and can be advanced manually.
- Stat Leaders includes clickable tabs and an arrow for Goals, Assists, Yellow Cards, and Red Cards.
- Leader categories advance every 7 seconds.


FONT + AUTO-SCROLL UPDATE
- All major fonts were enlarged.
- Group standings automatically scroll to the next two groups every 8 seconds.
- The transition uses a smooth vertical slide/fade.
- Manual next-page control still works.
