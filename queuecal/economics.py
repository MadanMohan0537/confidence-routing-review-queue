from __future__ import annotations

from .models import FieldPrediction, ThresholdPoint


def threshold_point(rows: list[FieldPrediction], threshold: float, review_hourly_cost: float = 30.0) -> ThresholdPoint:
    auto = [row for row in rows if row.confidence >= threshold]
    review = [row for row in rows if row.confidence < threshold]
    auto_errors = [row for row in auto if not row.correct]
    reviewer_hours = sum(row.review_minutes for row in review) / 60
    error_cost = sum(row.error_cost for row in auto_errors)
    return ThresholdPoint(
        threshold, len(auto) / len(rows), len(auto_errors), error_cost,
        len(review), reviewer_hours, error_cost + reviewer_hours * review_hourly_cost,
    )


def sweep(rows: list[FieldPrediction], thresholds: list[float] | None = None) -> list[ThresholdPoint]:
    return [threshold_point(rows, value) for value in (thresholds or [i / 20 for i in range(5, 20)])]


def economic_choice(points: list[ThresholdPoint]) -> ThresholdPoint:
    return min(points, key=lambda point: (point.total_cost, point.threshold))
