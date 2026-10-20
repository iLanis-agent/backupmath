# Backup Math

Backup retention and restore arithmetic. Keeping 30 days of restore points on 500 GB with a full copy every 7 days stores up to 3625 GB, which is 7.25 times the data.

## What it computes

All inputs are whole numbers.

- **The space truth** - data size in GB (1 to 100000), each incremental as a percent of it (0 to 100), a full copy every 1 to 60 days, and 1 to 400 days kept: the most full copies and incrementals the kept restore points can need (worst alignment of the keep window), and the storage in GB and as a multiple of the data. A full copy from before the window is kept when a point inside the window depends on it.
- **The restore truth** - the worst case restore reads the last full copy plus every incremental after it. Time at a restore speed in MB a second (1 GB counted as 1000 MB), rounded up to a whole second.
- **The reach truth** - how many days before a problem began the restore points still go, for a problem noticed some days after it began.

## Boundary

Arithmetic only. It has not seen any backup software, data or disks. It does not know about compression or deduplication, whether every incremental is the same size, whether backups are checked, or whether a restore will work, and it gives no verdict that a plan protects data. Every number is the owner's own entry.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic (exact integers).
- `oracle.py` - the Python mirror (replays the plan day by day for every window alignment, walks every restore chain) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (153 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/backupmath/
Repo: https://github.com/iLanis-agent/backupmath
