import unittest

from queuecal.calibration import calibrate
from queuecal.data import synthetic_receipts
from queuecal.delayed import (
    CorrectionLabel,
    decision_id,
    delayed_label_audit,
    synthetic_corrections,
)
from queuecal.demo import THRESHOLDS
from queuecal.demo import run_demo


class DelayedLabelTests(unittest.TestCase):
    def setUp(self):
        self.rows = calibrate(synthetic_receipts(count=30))
        self.labels = synthetic_corrections(self.rows)

    def test_decision_ids_are_stable_and_unique(self):
        ids = [decision_id(row) for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [label.decision_id for label in self.labels])

    def test_short_window_exposes_partial_observation(self):
        audit = delayed_label_audit(self.rows, self.labels, THRESHOLDS, window_days=1)
        self.assertEqual("PARTIAL_LABELS", audit["status"])
        self.assertLess(audit["label_coverage"], 1.0)
        self.assertEqual(0, audit["errors_observed"])

    def test_seven_day_window_recovers_every_seeded_error(self):
        audit = delayed_label_audit(self.rows, self.labels, THRESHOLDS, window_days=7)
        self.assertEqual(audit["error_denominator"], audit["errors_observed"])
        self.assertEqual(1.0, audit["error_observation_rate"])

    def test_complete_window_has_zero_threshold_regret(self):
        audit = delayed_label_audit(self.rows, self.labels, THRESHOLDS, window_days=14)
        self.assertEqual("COMPLETE", audit["status"])
        self.assertEqual(0.0, audit["threshold_regret"])
        self.assertEqual(audit["oracle_threshold"], audit["observed_threshold"])

    def test_empty_window_fails_closed_without_fake_regret(self):
        audit = delayed_label_audit(self.rows, self.labels, THRESHOLDS, window_days=0)
        self.assertEqual("INSUFFICIENT_LABELS", audit["status"])
        self.assertIsNone(audit["threshold_regret"])

    def test_duplicate_and_unknown_corrections_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate correction"):
            delayed_label_audit(self.rows, self.labels + [self.labels[0]], THRESHOLDS)
        unknown = CorrectionLabel("missing:field", False, 1)
        with self.assertRaisesRegex(ValueError, "unknown decision ID"):
            delayed_label_audit(self.rows, self.labels + [unknown], THRESHOLDS)

    def test_invalid_window_and_thresholds_are_rejected(self):
        with self.assertRaises(ValueError):
            delayed_label_audit(self.rows, self.labels, THRESHOLDS, window_days=-1)
        with self.assertRaises(ValueError):
            delayed_label_audit(self.rows, self.labels, [])

    def test_demo_exports_delay_windows_and_regret(self):
        audit = run_demo()["delayed_label_audit"]
        self.assertEqual({"day_1", "day_7", "day_14"}, set(audit))
        self.assertGreater(audit["day_1"]["threshold_regret"], 0)
        self.assertEqual(0.0, audit["day_14"]["threshold_regret"])

    def test_markdown_exposes_delay_denominators(self):
        markdown = run_demo()["markdown"]
        self.assertIn("## Delayed-label audit", markdown)
        self.assertIn("26/180", markdown)


if __name__ == "__main__":
    unittest.main()
