#!/usr/bin/env python3
"""Build a deterministic readiness and cost report from this portfolio's JSON data."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOL_FIELDS = (
    "setup_information_received", "power_required", "power_approved",
    "arrival_window_confirmed",
)
MONEY_FIELDS = (
    "planned_cents", "paid_cents", "committed_unpaid_cents",
    "remaining_estimate_cents",
)
BLOCKER_LABELS = {
    "setup_information": "Setup information missing",
    "power_approval": "Required power not approved",
    "booth_conflict": "Booth assigned to multiple confirmed vendors",
    "booth_assignment": "Booth unassigned",
    "arrival_window": "Arrival window unconfirmed",
}
NEXT_ACTIONS = {
    "setup_information": ("Request missing setup information", "Vendor coordinator"),
    "power_approval": ("Resolve the power request with logistics", "Logistics lead"),
    "booth_conflict": ("Resolve the shared booth assignment", "Logistics lead"),
    "booth_assignment": ("Assign a compatible available booth", "Logistics lead"),
    "arrival_window": ("Confirm the arrival window", "Vendor coordinator"),
}


def require_int(value, label, minimum=None):
    if type(value) is not int or (minimum is not None and value < minimum):
        suffix = "" if minimum is None else " >= " + str(minimum)
        raise ValueError(label + " must be an integer" + suffix)


def validate_vendors(data):
    require_int(data["as_of_day"], "as_of_day")
    inventory = data["booth_inventory"]
    if not inventory or len(inventory) != len(set(inventory)):
        raise ValueError("Booth inventory must contain unique booth identifiers")
    for key in ("setup_information", "confirmation", "power_approval", "booth_assignment", "arrival_window"):
        require_int(data["deadlines"][key], "deadline " + key)
    identifiers = set()
    for vendor in data["vendors"]:
        if vendor["id"] in identifiers:
            raise ValueError("Duplicate vendor ID: " + vendor["id"])
        identifiers.add(vendor["id"])
        if vendor["participation"] not in {"confirmed", "invited", "declined"}:
            raise ValueError("Invalid participation status: " + vendor["id"])
        for key in BOOL_FIELDS:
            if type(vendor[key]) is not bool:
                raise ValueError(key + " must be true or false: " + vendor["id"])
        booth = vendor["booth_id"]
        if booth is not None and booth not in inventory:
            raise ValueError("Unknown booth: " + str(booth))
        if booth is not None and vendor["participation"] != "confirmed":
            raise ValueError("Only confirmed vendors may hold a booth in this model")


def readiness_gaps(vendor, conflicting_booths):
    """Order gaps by dependency; one next action resolves the first gap."""
    gaps = []
    if not vendor["setup_information_received"]:
        gaps.append("setup_information")
    if vendor["power_required"] and not vendor["power_approved"]:
        gaps.append("power_approval")
    if vendor["booth_id"] in conflicting_booths:
        gaps.append("booth_conflict")
    if vendor["booth_id"] is None:
        gaps.append("booth_assignment")
    if not vendor["arrival_window_confirmed"]:
        gaps.append("arrival_window")
    return gaps


def analyze_vendors(data):
    validate_vendors(data)
    vendors = data["vendors"]
    as_of = data["as_of_day"]
    confirmed = [v for v in vendors if v["participation"] == "confirmed"]
    invited = [v for v in vendors if v["participation"] == "invited"]
    assignments = defaultdict(list)
    for vendor in confirmed:
        if vendor["booth_id"] is not None:
            assignments[vendor["booth_id"]].append(vendor["id"])
    conflicts = {booth: ids for booth, ids in assignments.items() if len(ids) > 1}
    rows, actions = [], []
    for vendor in vendors:
        status = vendor["participation"]
        gaps = readiness_gaps(vendor, conflicts) if status == "confirmed" else []
        row_status = "Ready" if status == "confirmed" and not gaps else (
            "Blocked" if status == "confirmed" else
            "Awaiting decision" if status == "invited" else "Declined"
        )
        rows.append({**vendor, "status": row_status, "gaps": gaps})
        if gaps:
            first = gaps[0]
            deadline_key = "booth_assignment" if first == "booth_conflict" else first
            due = data["deadlines"][deadline_key]
            priority = 1 if first in {"power_approval", "booth_conflict"} or due <= as_of else 2
            action, owner = NEXT_ACTIONS[first]
            actions.append({"vendor_id": vendor["id"], "vendor": vendor["name"],
                            "priority": priority, "action": action, "owner": owner,
                            "due_day": due, "overdue_days": max(0, as_of - due),
                            "reason": BLOCKER_LABELS[first]})
        elif status == "invited":
            due = data["deadlines"]["confirmation"]
            actions.append({"vendor_id": vendor["id"], "vendor": vendor["name"],
                            "priority": 3, "action": "Resolve invitation after capacity review",
                            "owner": "Outreach lead", "due_day": due,
                            "overdue_days": max(0, as_of - due),
                            "reason": "Participation is not confirmed"})
    capacity = len(data["booth_inventory"])
    headroom = max(0, capacity - len(confirmed))
    invitation_exposure = max(0, len(invited) - headroom)
    over_capacity = max(0, len(confirmed) - capacity)
    if over_capacity or invitation_exposure:
        reason = (str(over_capacity) + " confirmed vendors exceed capacity") if over_capacity else (
            str(len(invited)) + " invitations remain open for " + str(headroom) + " places"
        )
        actions.append({"vendor_id": "EVENT", "vendor": "Capacity review", "priority": 1,
                        "action": "Review commitments before confirming additional vendors",
                        "owner": "Event lead", "due_day": as_of, "overdue_days": 0,
                        "reason": reason})
    actions.sort(key=lambda item: (item["priority"], -item["overdue_days"], item["due_day"], item["vendor_id"]))
    counts = Counter(row["status"] for row in rows)
    return {"as_of_day": as_of, "rows": rows, "actions": actions, "conflicts": conflicts,
            "confirmed": len(confirmed), "invited": len(invited),
            "declined": counts["Declined"], "ready": counts["Ready"], "blocked": counts["Blocked"],
            "readiness_pct": 100 * counts["Ready"] / len(confirmed) if confirmed else None,
            "capacity": capacity, "headroom": headroom, "invitation_exposure": invitation_exposure,
            "over_capacity": over_capacity, "unique_assigned_booths": len(assignments),
            "confirmed_unassigned": sum(v["booth_id"] is None for v in confirmed)}


def analyze_budget(data):
    if data["currency"] != "USD":
        raise ValueError("This report formats USD only")
    require_int(data["contingency_cents"], "contingency_cents", 0)
    rows = []
    names = set()
    for category in data["categories"]:
        if category["name"] in names:
            raise ValueError("Duplicate budget category: " + category["name"])
        names.add(category["name"])
        for key in MONEY_FIELDS:
            require_int(category[key], category["name"] + " " + key, 0)
        forecast = category["paid_cents"] + category["committed_unpaid_cents"] + category["remaining_estimate_cents"]
        rows.append({**category, "forecast_cents": forecast,
                     "variance_cents": forecast - category["planned_cents"]})
    totals = {key: sum(row[key] for row in rows) for key in MONEY_FIELDS}
    forecast = sum(row["forecast_cents"] for row in rows)
    ceiling = totals["planned_cents"] + data["contingency_cents"]
    exposure = 0
    for item in data.get("stress_exposures", []):
        require_int(item["incremental_cents"], item["name"] + " incremental_cents", 0)
        exposure += item["incremental_cents"]
    return {"rows": rows, **totals, "forecast_cents": forecast,
            "variance_cents": forecast - totals["planned_cents"],
            "contingency_cents": data["contingency_cents"], "ceiling_cents": ceiling,
            "contingency_required_cents": max(0, forecast - totals["planned_cents"]),
            "headroom_cents": ceiling - forecast, "stress_exposure_cents": exposure,
            "stress_forecast_cents": forecast + exposure,
            "stress_headroom_cents": ceiling - forecast - exposure,
            "stress_exposures": data.get("stress_exposures", [])}


def dollars(cents, signed=False):
    sign = "-" if cents < 0 else "+" if signed and cents > 0 else ""
    return sign + "$" + format(abs(cents) / 100, ",.2f")


def relative_day(day):
    return "T" if day == 0 else "T+" + str(day) if day > 0 else "T" + str(day)


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(vendors, budget):
    pct = "n/a" if vendors["readiness_pct"] is None else format(vendors["readiness_pct"], ".1f") + "%"
    lines = ["# Event operations report", "",
             "Generated from the independent demonstration defined in the [case study](../README.md).",
             "", "## Readiness at " + relative_day(vendors["as_of_day"]), "",
             "| Measure | Result |", "|---|---:|",
             "| Confirmed vendors | " + str(vendors["confirmed"]) + " |",
             "| Ready confirmed vendors | " + str(vendors["ready"]) + " |",
             "| Blocked confirmed vendors | " + str(vendors["blocked"]) + " |",
             "| Readiness among confirmed vendors | " + pct + " |",
             "| Open invitations | " + str(vendors["invited"]) + " |",
             "| Declined invitations | " + str(vendors["declined"]) + " |",
             "| Booth capacity | " + str(vendors["capacity"]) + " |",
             "| Additional confirmed vendors capacity can support | " + str(vendors["headroom"]) + " |",
             "| Open invitations exceeding available places | " + str(vendors["invitation_exposure"]) + " |",
             "| Confirmed vendors without a booth | " + str(vendors["confirmed_unassigned"]) + " |",
             "| Unique booths currently assigned | " + str(vendors["unique_assigned_booths"]) + " |", "",
             "The readiness denominator includes confirmed vendors only. Invitations are not commitments. "
             "The capacity calculation uses confirmed demand, even when booth assignments are incomplete.", "",
             "## Assignment conflicts", ""]
    if vendors["conflicts"]:
        for booth, ids in sorted(vendors["conflicts"].items()):
            lines.append("- **" + cell(booth) + "** is assigned to " + ", ".join(ids) + ". Both vendors remain blocked until the conflict is resolved.")
    else:
        lines.append("No duplicate confirmed booth assignments.")
    if vendors["over_capacity"]:
        lines.extend(["", "Confirmed demand exceeds capacity by " + str(vendors["over_capacity"]) + "."])
    lines.extend(["", "## Prioritized next actions", "",
                  "One next action is shown per unresolved vendor, plus the necessary event-level capacity check. "
                  "The entire list is sorted by priority, then overdue days, deadline, and vendor ID.", "",
                  "| Rank | Priority | Record | Next action | Owner | Due | Days overdue | Reason |",
                  "|---:|---|---|---|---|---|---:|---|"])
    for rank, action in enumerate(vendors["actions"], 1):
        values = [rank, "P" + str(action["priority"]), action["vendor_id"] + " " + action["vendor"],
                  action["action"], action["owner"], relative_day(action["due_day"]),
                  action["overdue_days"], action["reason"]]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    lines.extend(["", "## Vendor detail", "",
                  "| ID | Vendor | Participation | Booth | Status | Remaining gaps |",
                  "|---|---|---|---|---|---|"])
    for row in vendors["rows"]:
        gaps = "; ".join(BLOCKER_LABELS[key] for key in row["gaps"]) or "None" if row["participation"] == "confirmed" else "Not assessed until confirmed"
        values = [row["id"], row["name"], row["participation"], row["booth_id"] or "Unassigned", row["status"], gaps]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    lines.extend(["", "## Budget forecast", "",
                  "Forecast equals paid costs plus committed but unpaid costs plus remaining estimates. "
                  "These are mutually exclusive cost states; moving a cost between states must not increase the total.", "",
                  "| Category | Planned | Paid | Committed unpaid | Remaining estimate | Forecast | Variance |",
                  "|---|---:|---:|---:|---:|---:|---:|"])
    for row in budget["rows"]:
        values = [row["name"]] + [dollars(row[key]) for key in (*MONEY_FIELDS, "forecast_cents")] + [dollars(row["variance_cents"], True)]
        lines.append("| " + " | ".join(values) + " |")
    values = ["**Total**"] + ["**" + dollars(budget[key]) + "**" for key in (*MONEY_FIELDS, "forecast_cents")] + ["**" + dollars(budget["variance_cents"], True) + "**"]
    lines.append("| " + " | ".join(values) + " |")
    lines.extend(["", "| Funding measure | Amount |", "|---|---:|",
                  "| Category plan | " + dollars(budget["planned_cents"]) + " |",
                  "| Contingency allowance | " + dollars(budget["contingency_cents"]) + " |",
                  "| Total spending ceiling | " + dollars(budget["ceiling_cents"]) + " |",
                  "| Baseline forecast | " + dollars(budget["forecast_cents"]) + " |",
                  "| Contingency required by baseline forecast | " + dollars(budget["contingency_required_cents"]) + " |",
                  "| Headroom against total ceiling | " + dollars(budget["headroom_cents"]) + " |", "",
                  "A positive category variance means forecast spending exceeds that category's plan. "
                  "Contingency is an allowance, not an additional expense to add to the forecast.", "",
                  "## Additional exposure scenario", ""])
    for item in budget["stress_exposures"]:
        lines.append("- " + cell(item["name"]) + ": " + dollars(item["incremental_cents"]) + " above the baseline forecast.")
    lines.extend(["", "Combined additional exposure is **" + dollars(budget["stress_exposure_cents"]) + "**, raising the forecast to **" + dollars(budget["stress_forecast_cents"]) + "**."])
    if budget["stress_headroom_cents"] < 0:
        lines.append("That scenario exceeds the spending ceiling by **" + dollars(-budget["stress_headroom_cents"]) + "**. Review the assumptions and secure an offset or additional funding before authorizing the full increase.")
    else:
        lines.append("That scenario leaves **" + dollars(budget["stress_headroom_cents"]) + "** of headroom.")
    lines.extend(["", "[Read the decision analysis](../docs/decision-analysis.md) · [Read the operating brief](../docs/operations-brief.md)", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "operations-report.md")
    args = parser.parse_args()
    vendors = analyze_vendors(json.loads((args.data_dir / "vendors.json").read_text()))
    budget = analyze_budget(json.loads((args.data_dir / "budget.json").read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(vendors, budget), encoding="utf-8")
    print("Wrote " + str(args.output))
    print("Ready: " + str(vendors["ready"]) + "/" + str(vendors["confirmed"]) +
          "; baseline forecast: " + dollars(budget["forecast_cents"]) +
          "; stress forecast: " + dollars(budget["stress_forecast_cents"]))


if __name__ == "__main__":
    main()
