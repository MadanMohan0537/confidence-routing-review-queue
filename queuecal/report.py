from __future__ import annotations

from .consistency import ConsistencyComparison
from .models import QueueResult, ThresholdPoint


def markdown_report(
    points: list[ThresholdPoint],
    baseline: QueueResult,
    capacity: QueueResult,
    sensitivity: list[dict],
    correlated: ConsistencyComparison,
) -> str:
    lines = ["# QueueCal threshold report", "", "## Threshold curve", "", "| Threshold | Automation | Auto errors | Error cost | Reviewer hours | Total cost |", "|---:|---:|---:|---:|---:|---:|"]
    for point in points:
        lines.append(f"| {point.threshold:.2f} | {point.automation_rate:.1%} | {point.auto_errors} | ${point.expected_error_cost:.2f} | {point.reviewer_hours:.2f} | ${point.total_cost:.2f} |")
    lines += ["", "## Surge comparison", "", "| Router | Threshold | Reviews | SLA breaches | Breach rate | Max wait | Total cost |", "|---|---:|---:|---:|---:|---:|---:|", f"| Economic-only | {baseline.threshold:.2f} | {baseline.reviewed} | {baseline.sla_breaches} | {baseline.breach_rate:.1%} | {baseline.max_wait_minutes:.1f} min | ${baseline.total_cost:.2f} |", f"| Capacity-aware | {capacity.threshold:.2f} | {capacity.reviewed} | {capacity.sla_breaches} | {capacity.breach_rate:.1%} | {capacity.max_wait_minutes:.1f} min | ${capacity.total_cost:.2f} |", "", "## Service-time sensitivity", ""]
    for row in sensitivity:
        lines.append(f"- {row['multiplier']}× service time: threshold {row['threshold']:.2f}, breach rate {row['breach_rate']:.1%}, total cost ${row['total_cost']:.2f}")
    ratio = (
        f"{correlated.added_reviews_per_caught_error:.2f}"
        if correlated.added_reviews_per_caught_error is not None
        else "not applicable"
    )
    lines += [
        "",
        "## Correlated amount-field review",
        "",
        "| Policy | Reviewed fields | Caught seeded errors |",
        "|---|---:|---:|",
        f"| Independent confidence | {correlated.baseline_reviewed_fields} | {correlated.baseline_caught_errors} |",
        f"| Arithmetic group rule | {correlated.grouped_reviewed_fields} | {correlated.grouped_caught_errors} |",
        "",
        f"- Additional errors caught: {correlated.additional_errors_caught}",
        f"- Extra field reviews: {correlated.extra_field_reviews}",
        f"- Added reviews per additional caught error: {ratio}",
        f"- False-positive group reviews: {correlated.false_positive_group_reviews}",
        f"- Predeclared acceptance passed: {correlated.acceptance_passed}",
        "",
        "> Synthetic data and assumed costs demonstrate the decision method; they do not establish production performance.",
    ]
    return "\n".join(lines) + "\n"

