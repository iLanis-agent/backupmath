// Backup Math engine: how much a full-plus-incremental backup plan stores, what a worst case restore reads, and how far back restore points reach. Exact integers.
function _int(t, err, lo, hi) {
  t = typeof t === "string" ? t.trim() : "";
  if (!/^[0-9]{1,7}$/.test(t)) throw new Error(err);
  var v = parseInt(t, 10);
  if (v < lo || v > hi) throw new Error(err);
  return v;
}
function _plural(n, one, many) { return n + " " + (n === 1 ? one : many); }
function _hund(h) { // integer hundredths to a decimal, trailing zeros dropped
  var s = String(Math.floor(h / 100)), f = h % 100;
  if (f === 0) return s;
  return s + "." + (f % 10 === 0 ? String(f / 10) : (f < 10 ? "0" + f : String(f)));
}
function _span(n) {
  var s = _plural(n, "second", "seconds");
  if (n < 60) return s;
  var d = Math.floor(n / 86400), h = Math.floor((n % 86400) / 3600), m = Math.floor((n % 3600) / 60), r = n % 60, p = [];
  if (d) p.push(_plural(d, "day", "days"));
  if (h) p.push(_plural(h, "hour", "hours"));
  if (m) p.push(_plural(m, "minute", "minutes"));
  if (r) p.push(_plural(r, "second", "seconds"));
  var t = p.length > 1 ? p.slice(0, -1).join(", ") + " and " + p[p.length - 1] : p[0];
  return s + " (" + t + ")";
}
var _SERR = "the data size must be a whole number of GB from 1 to 100000";
var _PERR = "the incremental size must be a whole number of percent from 0 to 100";
var _NERR = "the days between full copies must be a whole number from 1 to 60";
var _RERR = "the days kept must be a whole number from 1 to 400";

function spaceTruth(sizeGb, incPct, everyDays, keepDays) {
  var s = _int(sizeGb, _SERR, 1, 100000);
  var p = _int(incPct, _PERR, 0, 100);
  var n = _int(everyDays, _NERR, 1, 60);
  var r = _int(keepDays, _RERR, 1, 400);
  if (n === 1) {
    return "Keeping " + _plural(r, "day", "days") + " of restore points with a full copy every day stores " + _plural(r, "full copy", "full copies") + " and no incrementals. With " + s + " GB of data that is " + _hund(r * s * 100) + " GB, " + r + (r === 1 ? " time" : " times") + " the data.";
  }
  var fulls = 0, incs = 0, tot = -1;
  for (var o = 0; o < n; o++) { // the cycle day the oldest kept point falls on
    var inside = o === 0 ? Math.floor((r - 1) / n) + 1 : Math.floor((o + r - 1) / n) - Math.floor((o - 1) / n);
    var f = inside + (o > 0 ? 1 : 0), i = r - inside, t = f * s * 100 + i * s * p;
    if (t > tot || (t === tot && (f > fulls || (f === fulls && i > incs)))) { tot = t; fulls = f; incs = i; }
  }
  var ratio = fulls * 100 + incs * p;
  return "Keeping " + _plural(r, "day", "days") + " of restore points with a full copy every " + n + " days and an incremental on the other days stores up to " + _plural(fulls, "full copy", "full copies") + " and " + _plural(incs, "incremental", "incrementals") + ". With " + s + " GB of data and each incremental " + p + " percent of it, that is up to " + _hund(tot) + " GB, " + _hund(ratio) + (ratio === 100 ? " time" : " times") + " the data.";
}
function chainTruth(sizeGb, incPct, everyDays, mbPerSec) {
  var s = _int(sizeGb, _SERR, 1, 100000);
  var p = _int(incPct, _PERR, 0, 100);
  var n = _int(everyDays, _NERR, 1, 60);
  var m = _int(mbPerSec, "the restore speed must be a whole number of MB a second from 1 to 100000", 1, 100000);
  var read = s * 100 + (n - 1) * s * p; // hundredths of a GB
  var secs = Math.floor((read * 10 + m - 1) / m);
  var how = n === 1 ? "Every point is a full copy, so a restore reads the full copy" : "In the worst case a restore needs the last full copy and " + _plural(n - 1, "incremental", "incrementals") + ", which is";
  return how + (n === 1 ? ": " : " ") + _hund(read) + " GB to read. At " + m + " MB a second (1 GB counted as 1000 MB) that takes " + _span(secs) + ", rounded up to a whole second.";
}
function reachTruth(keepDays, agoDays) {
  var r = _int(keepDays, _RERR, 1, 400);
  var a = _int(agoDays, "the days since it began must be a whole number from 0 to 400", 0, 400);
  var head = "Restore points reach back " + _plural(r, "day", "days") + ". A problem that began " + (a === 0 ? "today" : _plural(a, "day", "days") + " ago");
  if (a >= r) return head + " is older than every restore point, so no point reaches back to before it began.";
  return head + " can be undone from points up to " + _plural(r - a, "day", "days") + " before it began.";
}
