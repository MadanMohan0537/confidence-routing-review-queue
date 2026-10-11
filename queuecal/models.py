from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldPrediction:
    item_id: str
    field: str
    confidence: float
    correct: bool
    error_cost: float
    arrival_minute: float
    review_minutes: float
    priority: int = 1


@dataclass(frozen=True)
class CalibrationBin:
    lower: float
    upper: float
    count: int
    mean_confidence: float
    accuracy: float


@dataclass(frozen=True)
class ThresholdPoint:
    threshold: float
    automation_rate: float
    auto_errors: int
    expected_error_cost: float
    review_count: int
    reviewer_hours: float
    total_cost: float


@dataclass(frozen=True)
class QueueResult:
    threshold: float
    reviewed: int
    sla_breaches: int
    breach_rate: float
    max_wait_minutes: float
    reviewer_utilization: float
    total_cost: float
