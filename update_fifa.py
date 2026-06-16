import asyncio, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

DATA = Path("data.json")
URL = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures"

ALIASES = {
    "Korea Republic":"Korea Republic","South Korea":"Korea Republic",
    "IR Iran":"Iran","Iran":"Iran","Côte d'Ivoire":"Ivory Coast",
    "Cabo Verde":"Cape Verde","Congo DR":"DR Congo","Türkiye":"Türkiye",
    "Curacao":"Curaçao","Curaçao":"Curaçao","USA":"USA","United States":"USA"
}

def norm(s):
    if not isinstance(s,str): return ""
    s=re.sub(r"\s+"," ",s).strip()
    return ALIASES.get(s,s)

def walk(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values(): yield from walk(v)
    elif isinstance(obj,list):
        for v in obj: yield from walk(v)

def value(d,*keys):
    for k in keys:
        if k in d and d[k] not in (None,""): return d[k]
    return None

def team_name(x):
    if isinstance(x,str): return norm(x)
    if isinstance(x,dict):
        return norm(value(x,"name","displayName","shortName","teamName","countryName","description") or "")
    return ""

def parse_match(d):
    home=value(d,"homeTeam","home","team1","competitor1")
    away=value(d,"awayTeam","away","team2","competitor2")
    hn,an=team_name(home),team_name(away)
    if not hn or not an: return None
    kickoff=value(d,"date","kickOffTime","kickoff","startTime","matchDate","utcDate")
    status=str(value(d,"status","matchStatus","state","phase") or "")
    hs=value(d,"homeScore","scoreHome","homeTeamScore")
    a_s=value(d,"awayScore","scoreAway","awayTeamScore")
    if isinstance(home,dict): hs=hs if hs is not None else value(home,"score","goals")
    if isinstance(away,dict): a_s=a_s if a_s is not None else value(away,"score","goals")
    group=str(value(d,"group","groupName","pool") or "")
    venue=value(d,"venue","stadium","venueName")
    if isinstance(venue,dict): venue=value(venue,"name","displayName")
    return {"kickoff":kickoff,"home":hn,"away":an,"homeScore":hs,"awayScore":a_s,
            "status":status,"group":group,"venue":venue or ""}

def finished(m):
    s=(m.get("status") or "").lower()
    return any(x in s for x in ("final","finished","complete","full time","ended"))

def group_letter(text):
    m=re.search(r"\b([A-L])\b",str(text))
    return m.group(1) if m else ""

def calculate(base,matches):
    by_team={}
    for letter,teams in base["groups"].items():
        for t in teams:
            t.update({"p":0,"w":0,"d":0,"l":0,"gf":0,"ga":0,"pts":0})
            by_team[t["team"]]=(letter,t)
    for m in matches:
        if not finished(m): continue
        if m["home"] not in by_team or m["away"] not in by_team: continue
        try: hs,as_=int(m["homeScore"]),int(m["awayScore"])
        except: continue
        lh,h=by_team[m["home"]]; la,a=by_team[m["away"]]
        if lh!=la: continue
        for t,gf,ga in ((h,hs,as_),(a,as_,hs)):
            t["p"]+=1;t["gf"]+=gf;t["ga"]+=ga
        if hs>as_: h["w"]+=1;h["pts"]+=3;a["l"]+=1
        elif as_>hs: a["w"]+=1;a["pts"]+=3;h["l"]+=1
        else: h["d"]+=1;a["d"]+=1;h["pts"]+=1;a["pts"]+=1
    return base

async def main():
    base=json.loads(DATA.read_text(encoding="utf-8"))
    captured=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        page=await browser.new_page(viewport={"width":1440,"height":1200})
        async def response(resp):
            try:
                ct=(resp.headers.get("content-type") or "").lower()
                if "json" in ct and ("fifa" in resp.url or "api" in resp.url):
                    payload=await resp.json()
                    captured.append(payload)
            except: pass
        page.on("response",response)
        await page.goto(URL,wait_until="networkidle",timeout=120000)
        await page.wait_for_timeout(8000)
        await browser.close()

    matches=[]
    seen=set()
    for payload in captured:
        for d in walk(payload):
            m=parse_match(d)
            if not m: continue
            key=(m["home"],m["away"],str(m["kickoff"]))
            if key in seen: continue
            seen.add(key);matches.append(m)

    if not matches:
        print("No structured FIFA match data found; preserving last-known-good data.")
        return

    updated=calculate(base,matches)
    future=[]
    now=datetime.now(timezone.utc)
    flag_by_team={t["team"]:t["flag"] for ts in updated["groups"].values() for t in ts}
    for m in matches:
        try:
            dt=datetime.fromisoformat(str(m["kickoff"]).replace("Z","+00:00"))
        except: continue
        if dt < now and finished(m): continue
        if m["home"] not in flag_by_team or m["away"] not in flag_by_team: continue
        future.append({
            "kickoff":dt.astimezone(timezone.utc).isoformat().replace("+00:00","Z"),
            "home":m["home"],"homeFlag":flag_by_team[m["home"]],
            "away":m["away"],"awayFlag":flag_by_team[m["away"]],
            "group":group_letter(m.get("group","")),
            "venue":m.get("venue",""),"status":m.get("status","")
        })
    future.sort(key=lambda x:x["kickoff"])
    if future: updated["games"]=future[:8]
    updated["source"]="Official FIFA scores & fixtures page"
    updated["updated"]=datetime.now(timezone.utc).isoformat()
    DATA.write_text(json.dumps(updated,indent=2,ensure_ascii=False),encoding="utf-8")
    print(f"Updated from FIFA: {len(matches)} matches found.")

asyncio.run(main())
