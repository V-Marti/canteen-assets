#!/usr/bin/env python3
"""Copies the current season's files from seasonal/<Season>/ over the live files in the repo root."""
import datetime, os, pathlib, shutil, sys
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEASONAL = ROOT / "seasonal"

def thanksgiving(year):
    nov1 = datetime.date(year, 11, 1)
    first_thu = 1 + (3 - nov1.weekday()) % 7          # Thursday = 3
    return datetime.date(year, 11, first_thu + 21)    # 4th Thursday

def season_for(d):
    tg = thanksgiving(d.year)
    if d.month == 10:                                   return "Halloween"     # Oct 1-31
    if d.month == 11 and d <= tg + datetime.timedelta(days=1): return "Thanksgiving"  # Nov 1 - day after
    if d.month in (11, 12):                             return "Winter"        # weekend after - Dec 31
    if d.month == 1 and d.day <= 15:                    return "New Year"      # Jan 1-15
    if d.month == 3 and d.day <= 17:                    return "St Patricks"   # Mar 1-17
    return "Default"

def main():
    override = os.environ.get("SEASON_DATE", "").strip()
    today = datetime.date.fromisoformat(override) if override else datetime.datetime.now(ZoneInfo("America/New_York")).date()
    season = season_for(today)
    src = SEASONAL / season
    if not src.is_dir():
        sys.exit(f"Missing folder: {src}")
    changed = []
    for f in sorted(src.iterdir()):
        if not f.is_file():
            continue
        dst = ROOT / f.name
        if not dst.exists() or dst.read_bytes() != f.read_bytes():
            shutil.copyfile(f, dst)
            changed.append(f.name)
    print(f"{today}: season = {season}; updated: {', '.join(changed) or 'nothing'}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as fh:
            fh.write(f"season={season}\n")

if __name__ == "__main__":
    main()
