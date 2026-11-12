"""Delayed-label coverage and threshold-regret auditing."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .economics import economic_choice, sweep, threshold_point
from .models import FieldPrediction


@dataclass(frozen=True)
class CorrectionLabel:
    decision_id: str
    correct: bool
    observed_after_days: float


def decision_id(row: FieldPrediction) -> str:
    return f"{row.item_id}:{row.field}"


def synthetic_corrections(rows: list[FieldPrediction]) -> list[CorrectionLabel]:
    """Frozen label-delay fixture with slower discovery for costly total errors."""
    labels = []
    for index, row in enumerate(rows):
        if not row.correct:
            delay = 5.0 if row.field == "total" else 2.0
        else:
            # Routine QA samples arrive early; most correct decisions remain latent.
            delay = 1.0 if index % 4 == 0 else 14.0
        labels.append(CorrectionLabel(decision_id(row), row.correct, delay))
    return labels


def _validated_labels(
    rows: list[FieldPrediction], labels: list[CorrectionLabel]
) -> dict[str, CorrectionLabel]:
    ids = [decision_id(row) for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError("rows must be non-empty with unique decision IDs")
    index: dict[str, CorrectionLabel] = {}
    for label in labels:
        if label.decision_id in index:
            raise ValueError(f"duplicate correction for {label.decision_id}")
        if label.decision_id not in ids:
            raise ValueError(f"unknown decision ID: {label.decision_id}")
        if not isfinite(label.observed_after_days) or label.observed_after_days < 0:
            raise ValueError("observed_after_days must be finite and non-negative")
        index[label.decision_id] = label
    return index


def delayed_label_audit(
    rows: list[FieldPrediction],
    labels: list[CorrectionLabel],
    thresholds: list[float],
    *,
    window_days: float = 7.0,
    review_hourly_cost: float = 30.0,
) -> dict:
    """Measure observation coverage and regret against eventual full truth."""
    if not isfinite(window_days) or window_days < 0:
        raise ValueError("window_days must be finite and non-negative")
    if not thresholds or any(not 0 <= value <= 1 for value in thresholds):
        raise ValueError("thresholds must be non-empty and in [0, 1]")
    label_index = _validated_labels(rows, labels)
    visible_ids = {
        label.decision_id
        for label in labels
        if label.observed_after_days <= window_days
    }
    visible = [row for row in rows if decision_id(row) in visible_ids]
    if not visible:
        return {
            "decision_denominator": len(rows),
            "labels_received": 0,
            "label_coverage": 0.0,
            "error_denominator": sum(not row.correct for row in rows),
            "errors_observed": 0,
            "error_observation_rate": 0.0,
            "window_days": window_days,
            "status": "INSUFFICIENT_LABELS",
            "observed_threshold": None,
            "oracle_threshold": economic_choice(sweep(rows, thresholds)).threshold,
            "observed_policy_full_cost": None,
            "oracle_full_cost": economic_choice(sweep(rows, thresholds)).total_cost,
            "threshold_regret": None,
        }

    # Rebuild labels from the immutable correction ledger rather than trusting
    # mutable row truth at join time.
    visible = [
        FieldPrediction(**{**row.__dict__, "correct": label_index[decision_id(row)].correct})
        for row in visible
    ]
    observed_choice = economic_choice(sweep(visible, thresholds))
    oracle_choice = economic_choice(sweep(rows, thresholds))
    observed_full = threshold_point(rows, observed_choice.threshold, review_hourly_cost)
    errors = [row for row in rows if not row.correct]
    errors_observed = sum(decision_id(row) in visible_ids for row in errors)
    return {
        "decision_denominator": len(rows),
        "labels_received": len(visible),
        "label_coverage": round(len(visible) / len(rows), 6),
        "error_denominator": len(errors),
        "errors_observed": errors_observed,
        "error_observation_rate": round(errors_observed / len(errors), 6) if errors else 1.0,
        "window_days": window_days,
        "status": "COMPLETE" if len(visible) == len(rows) else "PARTIAL_LABELS",
        "observed_threshold": observed_choice.threshold,
        "oracle_threshold": oracle_choice.threshold,
        "observed_policy_full_cost": observed_full.total_cost,
        "oracle_full_cost": oracle_choice.total_cost,
        "threshold_regret": round(observed_full.total_cost - oracle_choice.total_cost, 6),
    }
