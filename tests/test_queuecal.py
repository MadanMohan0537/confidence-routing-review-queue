import unittest
from dataclasses import replace

from queuecal.calibration import calibrate, calibration_bins, expected_calibration_error
from queuecal.data import synthetic_receipts
from queuecal.demo import THRESHOLDS, run_demo
from queuecal.economics import economic_choice, sweep, threshold_point
from queuecal.models import FieldPrediction
from queuecal.queue import capacity_aware_choice, simulate_queue
from queuecal.review import review_queue


class QueueCalTests(unittest.TestCase):
    def setUp(self):
        self.raw = synthetic_receipts(count=30)
        self.rows = calibrate(self.raw)

    def test_fixture_is_reproducible(self):
        self.assertEqual(self.raw, synthetic_receipts(count=30))

    def test_three_fields_per_receipt(self):
        self.assertEqual(90, len(self.raw))

    def test_calibration_preserves_labels(self):
        self.assertEqual([r.correct for r in self.raw], [r.correct for r in self.rows])

    def test_calibration_improves_ece(self):
        self.assertLessEqual(expected_calibration_error(self.rows), expected_calibration_error(self.raw))

    def test_bins_record_denominators(self):
        self.assertEqual(len(self.raw), sum(group.count for group in calibration_bins(self.raw)))

    def test_threshold_extremes(self):
        low = threshold_point(self.rows, 0.0)
        high = threshold_point(self.rows, 1.0)
        self.assertEqual(1.0, low.automation_rate)
        self.assertEqual(0.0, high.automation_rate)

    def test_more_review_at_higher_threshold(self):
        points = sweep(self.rows, [0.5, 0.8])
        self.assertLessEqual(points[0].review_count, points[1].review_count)

    def test_total_cost_is_components(self):
        point = threshold_point(self.rows, 0.7)
        self.assertAlmostEqual(point.expected_error_cost + point.reviewer_hours * 30, point.total_cost)

    def test_economic_choice_returns_candidate(self):
        points = sweep(self.rows, THRESHOLDS)
        self.assertIn(economic_choice(points), points)

    def test_invalid_reviewer_count(self):
        with self.assertRaises(ValueError):
            simulate_queue(self.rows, 0.7, reviewers=0)

    def test_no_review_has_no_breaches(self):
        result = simulate_queue(self.rows, 0.0)
        self.assertEqual(0, result.sla_breaches)
        self.assertEqual(0.0, result.breach_rate)

    def test_priority_queue_orders_high_cost_first(self):
        preview = review_queue(self.rows, 1.0)
        priorities = [row["priority"] for row in preview]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

    def test_capacity_choice_meets_sla_when_feasible(self):
        surge = calibrate(synthetic_receipts(count=30, arrival_scale=3.0))
        choice = capacity_aware_choice(surge, THRESHOLDS, reviewers=2)
        feasible = [simulate_queue(surge, t, reviewers=2) for t in THRESHOLDS if simulate_queue(surge, t, reviewers=2).breach_rate <= 0.05]
        if feasible:
            self.assertLessEqual(choice.breach_rate, 0.05)

    def test_service_time_sensitivity_changes_wait(self):
        base = simulate_queue(self.rows, 0.75, reviewers=1)
        slower = simulate_queue([replace(r, review_minutes=r.review_minutes * 2) for r in self.rows], 0.75, reviewers=1)
        self.assertGreaterEqual(slower.max_wait_minutes, base.max_wait_minutes)

    def test_demo_records_sensitivity(self):
        self.assertEqual(3, len(run_demo()["sensitivity"]))

    def test_demo_capacity_does_not_increase_breaches(self):
        report = run_demo()
        self.assertLess(report["capacity_aware"].sla_breaches, report["baseline"].sla_breaches)

    def test_demo_exports_markdown(self):
        self.assertIn("## Surge comparison", run_demo()["markdown"])


if __name__ == "__main__":
    unittest.main()
