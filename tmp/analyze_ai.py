import json
import sys
from collections import Counter, defaultdict

path = r"D:\OneDrive\git_work\dev-workspace\tmp\ai_latest.json"
d = json.load(open(path, encoding="utf-8"))

print(f"manufacturer = {d['manufacturer']}")
print(f"resolvedUrl  = {d['resolvedUrl']}")
print(f"pageTitle    = {d['pageTitle']}")
print(f"category     = {d['category']}")
print(f"requestId    = {d['requestId']}")
print(f"rowsCount    = {d['rowsCount']}, len(rows) = {len(d['rows'])}")
print(f"usage        = {d.get('usage')}")
print()

print("-- rows --")
for r in d["rows"]:
    ln = r.get("length") or {}
    ft = ln.get("ft"); inc = ln.get("in")
    lw = r.get("lureWeightOz") or {}
    lwmin = lw.get("min"); lwmax = lw.get("max")
    mr = r.get("missingRequired") or []
    mo = r.get("missingOptional") or []
    print(f"{r['row']:>3} | {r.get('genre',''):<5} | {r['seriesName']:<14} | {r['modelName']:<16} | {ft}'{inc}\" | {lwmin}-{lwmax} | missReq={mr} missOpt={mo}")

print()
print("-- rows per series --")
for s, c in Counter(r["seriesName"] for r in d["rows"]).most_common():
    print(f"  {s}: {c}")

print()
print("-- rows per genre --")
for g, c in Counter(r.get("genre", "") for r in d["rows"]).most_common():
    print(f"  {g}: {c}")

print()
print("-- duplicates (exact series+model) --")
dups = Counter((r["seriesName"], r["modelName"]) for r in d["rows"])
any_dup = False
for k, v in dups.items():
    if v > 1:
        any_dup = True
        print(f"  DUP {k} x {v}")
if not any_dup:
    print("  (none)")

print()
print("-- duplicates ignoring separators (・,-,/,space,.) --")
import re
sep_re = re.compile(r"[\s・･.／/_-]+")
normed = defaultdict(list)
for r in d["rows"]:
    key = (r["seriesName"], sep_re.sub("", r["modelName"]))
    normed[key].append(r["modelName"])
any2 = False
for k, vals in normed.items():
    if len(vals) > 1:
        any2 = True
        print(f"  DUP-NORM {k}: {vals}")
if not any2:
    print("  (none)")

print()
print("-- missing length.in --")
for r in d["rows"]:
    ln = r.get("length") or {}
    if ln.get("in") is None:
        print(f"  row={r['row']} series={r['seriesName']} model={r['modelName']} length={ln}")

print()
print("-- missingRequired summary --")
mr_count = Counter()
for r in d["rows"]:
    for m in (r.get("missingRequired") or []):
        mr_count[m] += 1
for k, v in mr_count.most_common():
    print(f"  {k}: {v}")

print()
print("-- seriesName uniqueness --")
series_set = sorted(set(r["seriesName"] for r in d["rows"]))
for s in series_set:
    cnt = sum(1 for r in d["rows"] if r["seriesName"] == s)
    print(f"  {s}: {cnt} rows")
