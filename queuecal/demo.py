from __future__ import annotations

from dataclasses import replace

from .calibration import calibrate, expected_calibration_error
from .consistency import compare_correlated_review, synthetic_amount_receipts
from .data import synthetic_receipts
from .economics import economic_choice, sweep
from .queue import capacity_aware_choice, simulate_queue
from .report import markdown_report
from .review import review_queue


THRESHOLDS = [0.45, 0.55, 0.65, 0.75, 0.85, 0.90]


def run_demo() -> dict:
    raw = synthetic_receipts()
    calibrated = calibrate(raw)
    points = sweep(calibrated, THRESHOLDS)
    economical = economic_choice(points)
    surge = synthetic_receipts(arrival_scale=3.0)
    surge_calibrated = calibrate(surge)
    baseline = simulate_queue(surge_calibrated, economical.threshold, reviewers=2)
    capacity = capacity_aware_choice(surge_calibrated, THRESHOLDS, reviewers=2)
    sensitivity = []
    for multiplier in (0.75, 1.0, 1.5):
        variant = [replace(row, review_minutes=row.review_minutes * multiplier) for row in surge_calibrated]
        result = capacity_aware_choice(variant, THRESHOLDS, reviewers=2)
        sensitivity.append({"multiplier": multiplier, "threshold": result.threshold, "breach_rate": result.breach_rate, "total_cost": result.total_cost})
    correlated = compare_correlated_review(synthetic_amount_receipts())
    return {
        "records": len(calibrated),
        "raw_ece": expected_calibration_error(raw),
        "calibrated_ece": expected_calibration_error(calibrated),
        "economic_threshold": economical.threshold,
        "baseline": baseline,
        "capacity_aware": capacity,
        "sla_breaches_avoided": baseline.sla_breaches - capacity.sla_breaches,
        "sensitivity": sensitivity,
        "queue_preview": review_queue(calibrated, capacity.threshold)[:10],
        "correlated_review": correlated,
        "markdown": markdown_report(points, baseline, capacity, sensitivity, correlated),
    }

