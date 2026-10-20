#!/usr/bin/env python3
# Backup Math oracle - mirrors engine.js by simulation: a plan is replayed day by day for every possible alignment of the keep window, counting the full copies and incrementals the restore points need; restores are replayed by walking the chain; spans use repeated division.
import json, re, random
from fractions import Fraction as F
import math

def num(t, err, lo, hi):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"[0-9]{1,7}", t) or not lo <= int(t) <= hi: raise ValueError(err)
    return int(t)
def pl(n, a, b): return f"{n} {a if n == 1 else b}"
def dec(fr):
    v = fr * 100
    assert v.denominator == 1
    ip, fp = divmod(int(v), 100)
    s = f"{fp:02d}".rstrip("0")
    return f"{ip}.{s}" if s else str(ip)
def span(n):
    out = pl(n, "second", "seconds")
    if n < 60: return out
    parts = []; rest = n
    for size, a, b in [(86400, "day", "days"), (3600, "hour", "hours"), (60, "minute", "minutes"), (1, "second", "seconds")]:
        k = 0
        while rest >= size: rest -= size; k += 1
        if k: parts.append(pl(k, a, b))
    text = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"{out} ({text})"
SERR = "the data size must be a whole number of GB from 1 to 100000"
PERR = "the incremental size must be a whole number of percent from 0 to 100"
NERR = "the days between full copies must be a whole number from 1 to 60"
RERR = "the days kept must be a whole number from 1 to 400"

def worst_space(s, p, n, r):
    best = None
    for off in range(n):  # which day of the cycle the oldest kept point falls on
        days = range(off, off + r)
        fulls_needed = set(); incs = 0
        for d in days:
            last_full = d - (d % n)
            fulls_needed.add(last_full)
            if d % n != 0: incs += 1
        tot = len(fulls_needed) * F(s) + incs * F(s) * F(p, 100)
        cand = (tot, len(fulls_needed), incs)
        if best is None or cand > best: best = cand
    return best

def space(s, p, n, r):
    s = num(s, SERR, 1, 100000); p = num(p, PERR, 0, 100); n = num(n, NERR, 1, 60); r = num(r, RERR, 1, 400)
    tot, f, i = worst_space(s, p, n, r)
    if n == 1:
        return f"Keeping {pl(r,'day','days')} of restore points with a full copy every day stores {pl(f,'full copy','full copies')} and no incrementals. With {s} GB of data that is {dec(tot)} GB, {f} {'time' if f == 1 else 'times'} the data."
    ratio = tot / s
    return f"Keeping {pl(r,'day','days')} of restore points with a full copy every {n} days and an incremental on the other days stores up to {pl(f,'full copy','full copies')} and {pl(i,'incremental','incrementals')}. With {s} GB of data and each incremental {p} percent of it, that is up to {dec(tot)} GB, {dec(ratio)} {'time' if ratio == 1 else 'times'} the data."
def chain(s, p, n, m):
    s = num(s, SERR, 1, 100000); p = num(p, PERR, 0, 100); n = num(n, NERR, 1, 60)
    m = num(m, "the restore speed must be a whole number of MB a second from 1 to 100000", 1, 100000)
    worst = F(0)
    for day in range(n):  # restore the point `day` days after a full
        read = F(s)
        for _ in range(day): read += F(s) * F(p, 100)
        worst = max(worst, read)
    mb = worst * 1000
    secs = int(mb // m)  # start from the floor, then step up until the restore has finished
    while secs * m < mb: secs += 1
    how = "Every point is a full copy, so a restore reads the full copy: " if n == 1 else f"In the worst case a restore needs the last full copy and {pl(n-1,'incremental','incrementals')}, which is "
    return f"{how}{dec(worst)} GB to read. At {m} MB a second (1 GB counted as 1000 MB) that takes {span(secs)}, rounded up to a whole second."
def reach(r, a):
    r = num(r, RERR, 1, 400); a = num(a, "the days since it began must be a whole number from 0 to 400", 0, 400)
    head = f"Restore points reach back {pl(r,'day','days')}. A problem that began " + ("today" if a == 0 else f"{pl(a,'day','days')} ago")
    before = [d for d in range(r) if d > a]  # day offsets before today covered... counted as days earlier than the start
    covered = sum(1 for k in range(1, r + 1) if k - 1 >= a)  # point k days back lies before the start if k > a
    covered = len([k for k in range(0, r + 1) if k > a]) if False else max(0, r - a)
    if a >= r: return head + " is older than every restore point, so no point reaches back to before it began."
    return head + f" can be undone from points up to {pl(covered,'day','days')} before it began."

FNS = {"spaceTruth": space, "chainTruth": chain, "reachTruth": reach}

def cases():
    c = []
    for a in [("500","5","7","30"),("500","5","1","30"),("1","0","1","1"),("1","0","2","1"),("1","100","7","7"),("1","100","7","8"),("100","10","7","6"),("100","10","7","14"),("100","10","7","15"),("100","10","30","10"),("100000","100","60","400"),("100000","0","60","400"),
              ("250","3","7","28"),("999","7","3","10"),("10","1","2","2"),("10","1","2","3"),("10","50","5","5"),("10","50","5","1"),("7","33","4","9"),
              ("0","5","7","30"),("100001","5","7","30"),("x","5","7","30"),("500","101","7","30"),("500","-1","7","30"),("500","5","0","30"),("500","5","61","30"),("500","5","7","0"),("500","5","7","401"),("500","5","7",""),(" 500 "," 5 "," 7 "," 30 "),("5.5","5","7","30")]:
        c.append(("spaceTruth", list(a)))
    for a in [("500","5","7","200"),("1","0","1","100000"),("1","0","1","1"),("100000","100","60","1"),("100000","100","60","100000"),("100","10","2","7"),("333","7","5","13"),("1","1","3","3"),("10","50","7","1000"),
              ("0","5","7","200"),("500","101","7","200"),("500","5","0","200"),("500","5","7","0"),("500","5","7","100001"),("500","5","7","x"),("500","5","61","200"),(" 40 "," 4 "," 4 "," 40 ")]:
        c.append(("chainTruth", list(a)))
    for a in [("30","10"),("30","0"),("30","29"),("30","30"),("30","31"),("1","0"),("1","1"),("400","399"),("400","400"),("400","0"),("7","1"),("2","1"),
              ("0","3"),("401","3"),("30","401"),("30","-1"),("x","3"),("30",""),(" 30 "," 10 "),("5","4")]:
        c.append(("reachTruth", list(a)))
    r = random.Random(702)
    for _ in range(40):
        c.append(("spaceTruth", [str(r.randint(1, 100000)), str(r.randint(0, 100)), str(r.randint(1, 60)), str(r.randint(1, 400))]))
    for _ in range(25):
        c.append(("chainTruth", [str(r.randint(1, 100000)), str(r.randint(0, 100)), str(r.randint(1, 60)), str(r.randint(1, 100000))]))
    for _ in range(20):
        c.append(("reachTruth", [str(r.randint(1, 400)), str(r.randint(0, 400))]))
    return c

out = []
for fn, args in cases():
    try: exp = FNS[fn](*args)
    except ValueError as e: exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1); f.write("\n")
print(len(out), "cases written")
