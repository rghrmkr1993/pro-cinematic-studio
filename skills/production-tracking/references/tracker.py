#!/usr/bin/env python3
"""Shot tracker report. Standard library only.

Usage:
  python tracker.py shots.csv [--budgets scene_budgets.csv] [--today YYYY-MM-DD]

Reads the shot tracker CSV (see shot-tracker-template.csv) and prints:
  1. status counts (planned, prompted, drafted, approved, final, other)
  2. credits spent versus budget, per scene and in total, with a text burn bar
  3. overdue shots (due_date before today and status not approved or final)
Exit code 0 on success, 2 on a missing file or missing required columns.
Never calls any network or generation service.
"""
import csv
import sys
from collections import OrderedDict
from datetime import date, datetime

STATUSES = ["planned", "prompted", "drafted", "approved", "final"]
DONE = {"approved", "final"}
REQUIRED = ["shot_id", "scene", "status", "credits_est", "credits_actual", "due_date"]


def num(value):
    """Parse a number; blank or invalid becomes 0.0."""
    try:
        return float(str(value).strip().replace(",", ""))
    except (ValueError, TypeError):
        return 0.0


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("missing columns: " + ", ".join(missing))
        return [
            {k.strip(): (v or "").strip() for k, v in row.items() if k}
            for row in reader
            if any((v or "").strip() for v in row.values())
        ]


def read_budgets(path):
    budgets = {}
    with open(path, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            scene = (row.get("scene") or "").strip()
            if scene:
                budgets[scene] = num(row.get("credit_budget"))
    return budgets


def bar(spent, budget, width=20):
    if budget <= 0:
        return "[" + "?" * width + "] no budget"
    ratio = spent / budget
    filled = min(width, int(round(ratio * width)))
    flag = " OVER" if ratio > 1 else ""
    return "[" + "#" * filled + "." * (width - filled) + "] %3.0f%%%s" % (ratio * 100, flag)


def main(argv):
    args = argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    path = args[0]
    budget_path = None
    today = date.today()
    i = 1
    while i < len(args):
        if args[i] == "--budgets" and i + 1 < len(args):
            budget_path = args[i + 1]
            i += 2
        elif args[i] == "--today" and i + 1 < len(args):
            parsed = parse_date(args[i + 1])
            if parsed is None:
                print("bad --today date, use YYYY-MM-DD")
                return 2
            today = parsed
            i += 2
        else:
            print("unknown argument: " + args[i])
            return 2
    try:
        rows = read_rows(path)
        budgets = read_budgets(budget_path) if budget_path else {}
    except (OSError, ValueError) as exc:
        print("error: %s" % exc)
        return 2

    print("SHOT TRACKER REPORT  (%s)  shots: %d" % (today.isoformat(), len(rows)))

    print("\nStatus counts")
    counts = OrderedDict((s, 0) for s in STATUSES)
    other = 0
    for row in rows:
        status = row["status"].lower()
        if status in counts:
            counts[status] += 1
        else:
            other += 1
    total = len(rows) or 1
    for status, n in counts.items():
        print("  %-9s %4d  %5.1f%%" % (status, n, 100.0 * n / total))
    if other:
        print("  %-9s %4d  (unknown status values)" % ("other", other))
    done = counts["approved"] + counts["final"]
    print("  complete (approved or final): %d of %d" % (done, len(rows)))

    print("\nCredits (spent = credits_actual, estimate = credits_est, budget from --budgets or the estimate)")
    scenes = OrderedDict()
    for row in rows:
        s = scenes.setdefault(row["scene"] or "(none)", {"est": 0.0, "act": 0.0, "n": 0})
        s["est"] += num(row["credits_est"])
        s["act"] += num(row["credits_actual"])
        s["n"] += 1
    tot_est = tot_act = tot_bud = 0.0
    for scene, s in scenes.items():
        budget = budgets.get(scene, s["est"])
        tot_est += s["est"]
        tot_act += s["act"]
        tot_bud += budget
        print("  %-8s shots %3d  est %8.0f  spent %8.0f  budget %8.0f  %s"
              % (scene, s["n"], s["est"], s["act"], budget, bar(s["act"], budget)))
    print("  %-8s shots %3d  est %8.0f  spent %8.0f  budget %8.0f  %s"
          % ("TOTAL", len(rows), tot_est, tot_act, tot_bud, bar(tot_act, tot_bud)))
    if tot_bud > 0 and done > 0:
        per_done = tot_act / done
        remaining = len(rows) - done
        print("  spend per completed shot %.0f; projected total at that rate %.0f (estimate)"
              % (per_done, per_done * len(rows)))
        if remaining:
            print("  shots remaining: %d" % remaining)

    print("\nOverdue shots (due before %s, not approved or final)" % today.isoformat())
    overdue = []
    for row in rows:
        due = parse_date(row["due_date"])
        if due and due < today and row["status"].lower() not in DONE:
            overdue.append((due, row))
    overdue.sort(key=lambda item: item[0])
    if not overdue:
        print("  none")
    for due, row in overdue:
        print("  %-16s scene %-6s status %-9s due %s  (%d days late)  owner %s"
              % (row["shot_id"], row["scene"], row["status"], due.isoformat(),
                 (today - due).days, row.get("owner", "") or "unassigned"))

    bad_dates = [r["shot_id"] for r in rows if r["due_date"] and parse_date(r["due_date"]) is None]
    if bad_dates:
        print("\nWarning: unreadable due_date on: " + ", ".join(bad_dates))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
