"""Business-rule checks for event readiness, capacity, and expense forecasting."""

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_report import analyze_budget, analyze_vendors


class ReadinessRules(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "data" / "vendors.json").read_text())

    def test_supplied_scenario_counts_confirmed_and_ready_separately(self):
        result = analyze_vendors(self.data)
        self.assertEqual((result["confirmed"], result["ready"], result["blocked"]), (12, 6, 6))
        self.assertEqual(result["readiness_pct"], 50.0)
        self.assertEqual(result["conflicts"], {"B06": ["V006", "V007"]})

    def test_no_confirmed_vendors_has_no_readiness_percentage(self):
        self.data["vendors"] = [v for v in self.data["vendors"] if v["participation"] != "confirmed"]
        result = analyze_vendors(self.data)
        self.assertEqual(result["ready"], 0)
        self.assertEqual(result["confirmed"], 0)
        self.assertIsNone(result["readiness_pct"])

    def test_power_approval_is_required_only_when_power_is_requested(self):
        vendor = copy.deepcopy(self.data["vendors"][0])
        self.data["vendors"] = [vendor]
        self.assertEqual(analyze_vendors(self.data)["ready"], 1)
        vendor["power_required"] = True
        result = analyze_vendors(self.data)
        self.assertEqual(result["ready"], 0)
        self.assertIn("power_approval", result["rows"][0]["gaps"])
        vendor["power_approved"] = True
        self.assertEqual(analyze_vendors(self.data)["ready"], 1)

    def test_missing_setup_is_actioned_before_downstream_booth_and_arrival_gaps(self):
        self.data["vendors"] = [copy.deepcopy(self.data["vendors"][4])]
        result = analyze_vendors(self.data)
        self.assertEqual(result["rows"][0]["gaps"], ["setup_information", "booth_assignment", "arrival_window"])
        self.assertEqual(len(result["actions"]), 1)
        self.assertEqual(result["actions"][0]["action"], "Request missing setup information")

    def test_resolving_one_duplicate_assignment_unblocks_both_vendors(self):
        before = analyze_vendors(self.data)
        self.data["vendors"][6]["booth_id"] = "B07"
        after = analyze_vendors(self.data)
        self.assertEqual(after["ready"], before["ready"] + 2)
        self.assertEqual(after["conflicts"], {})

    def test_open_invitations_cannot_be_treated_as_free_confirmed_capacity(self):
        result = analyze_vendors(self.data)
        self.assertEqual((result["headroom"], result["invited"], result["invitation_exposure"]), (2, 3, 1))
        self.data["vendors"][12]["participation"] = "confirmed"
        result = analyze_vendors(self.data)
        self.assertEqual((result["confirmed"], result["ready"], result["headroom"]), (13, 6, 1))
        self.assertEqual(result["invitation_exposure"], 1)

    def test_unassigned_confirmed_vendors_still_consume_event_capacity(self):
        for vendor in self.data["vendors"]:
            vendor["participation"] = "confirmed"
        result = analyze_vendors(self.data)
        self.assertEqual(result["over_capacity"], 2)
        self.assertEqual(result["headroom"], 0)
        self.assertTrue(any(a["vendor_id"] == "EVENT" for a in result["actions"]))

    def test_priority_order_and_declined_exclusion(self):
        actions = analyze_vendors(self.data)["actions"]
        self.assertEqual([a["vendor_id"] for a in actions[:2]], ["V005", "V008"])
        self.assertNotIn("V016", [a["vendor_id"] for a in actions])
        self.assertEqual(actions[0]["overdue_days"], 4)

    def test_invalid_booth_and_duplicate_identifier_are_rejected(self):
        bad = copy.deepcopy(self.data)
        bad["vendors"][0]["booth_id"] = "B99"
        with self.assertRaises(ValueError):
            analyze_vendors(bad)
        bad = copy.deepcopy(self.data)
        bad["vendors"][1]["id"] = bad["vendors"][0]["id"]
        with self.assertRaises(ValueError):
            analyze_vendors(bad)


class BudgetRules(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "data" / "budget.json").read_text())

    def test_baseline_and_incremental_exposure_against_ceiling(self):
        result = analyze_budget(self.data)
        self.assertEqual(result["planned_cents"], 120000)
        self.assertEqual(result["forecast_cents"], 123500)
        self.assertEqual(result["ceiling_cents"], 135000)
        self.assertEqual(result["headroom_cents"], 11500)
        self.assertEqual(result["stress_forecast_cents"], 136500)
        self.assertEqual(result["stress_headroom_cents"], -1500)
        supplies = next(row for row in result["rows"] if row["name"] == "Event supplies")
        self.assertEqual(supplies["variance_cents"], 4000)

    def test_paying_an_existing_commitment_does_not_inflate_forecast(self):
        before = analyze_budget(self.data)
        equipment = next(row for row in self.data["categories"] if row["name"] == "Equipment")
        equipment["paid_cents"] += equipment["committed_unpaid_cents"]
        equipment["committed_unpaid_cents"] = 0
        after = analyze_budget(self.data)
        self.assertEqual(after["forecast_cents"], before["forecast_cents"])
        self.assertEqual(after["stress_forecast_cents"], before["stress_forecast_cents"])

    def test_negative_and_fractional_cents_are_rejected(self):
        for invalid in (-1, 100.5, True):
            with self.subTest(invalid=invalid):
                bad = copy.deepcopy(self.data)
                bad["categories"][0]["paid_cents"] = invalid
                with self.assertRaises(ValueError):
                    analyze_budget(bad)


if __name__ == "__main__":
    unittest.main()
