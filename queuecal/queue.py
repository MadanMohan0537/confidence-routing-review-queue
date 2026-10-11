from __future__ import annotations

import heapq

from .models import FieldPrediction, QueueResult


def simulate_queue(
    rows: list[FieldPrediction], threshold: float, reviewers: int = 2,
    sla_minutes: float = 20.0, review_hourly_cost: float = 30.0,
) -> QueueResult:
    if reviewers < 1:
        raise ValueError("reviewers must be positive")
    review = sorted((row for row in rows if row.confidence < threshold), key=lambda r: (r.arrival_minute, -r.priority, r.item_id, r.field))
    available = [0.0] * reviewers
    heapq.heapify(available)
    breaches = 0
    max_wait = 0.0
    service = 0.0
    for row in review:
        free = heapq.heappop(available)
        start = max(free, row.arrival_minute)
        wait = start - row.arrival_minute
        breaches += wait > sla_minutes
        max_wait = max(max_wait, wait)
        service += row.review_minutes
        heapq.heappush(available, start + row.review_minutes)
    horizon = max((row.arrival_minute for row in rows), default=0.0)
    finish = max(available, default=0.0)
    active_window = max(horizon, finish, 1.0)
    utilization = min(1.0, service / (reviewers * active_window))
    auto_errors = [row for row in rows if row.confidence >= threshold and not row.correct]
    cost = sum(row.error_cost for row in auto_errors) + service / 60 * review_hourly_cost
    return QueueResult(threshold, len(review), breaches, breaches / len(review) if review else 0.0, max_wait, utilization, cost)


def capacity_aware_choice(
    rows: list[FieldPrediction], thresholds: list[float], reviewers: int,
    max_breach_rate: float = 0.05,
) -> QueueResult:
    results = [simulate_queue(rows, value, reviewers) for value in thresholds]
    feasible = [result for result in results if result.breach_rate <= max_breach_rate]
    if feasible:
        return min(feasible, key=lambda result: (result.total_cost, result.breach_rate, result.threshold))
    # When every candidate violates the SLA, degrade explicitly toward the
    # least-bad breach rate instead of hiding overload behind a cheap choice.
    return min(results, key=lambda result: (result.breach_rate, result.total_cost, result.threshold))
