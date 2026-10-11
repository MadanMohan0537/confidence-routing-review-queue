from __future__ import annotations

from .models import QueueResult, ThresholdPoint


def markdown_report(points: list[ThresholdPoint], baseline: QueueResult, capacity: QueueResult, sensitivity: list[dict]) -> str:
    lines = ["# QueueCal threshold report", "", "## Threshold curve", "", "| Threshold | Automation | Auto errors | Error cost | Reviewer hours | Total cost |", "|---:|---:|---:|---:|---:|---:|"]
    for point in points:
        lines.append(f"| {point.threshold:.2f} | {point.automation_rate:.1%} | {point.auto_errors} | ${point.expected_error_cost:.2f} | {point.reviewer_hours:.2f} | ${point.total_cost:.2f} |")
    lines += ["", "## Surge comparison", "", "| Router | Threshold | Reviews | SLA breaches | Breach rate | Max wait | Total cost |", "|---|---:|---:|---:|---:|---:|---:|", f"| Economic-only | {baseline.threshold:.2f} | {baseline.reviewed} | {baseline.sla_breaches} | {baseline.breach_rate:.1%} | {baseline.max_wait_minutes:.1f} min | ${baseline.total_cost:.2f} |", f"| Capacity-aware | {capacity.threshold:.2f} | {capacity.reviewed} | {capacity.sla_breaches} | {capacity.breach_rate:.1%} | {capacity.max_wait_minutes:.1f} min | ${capacity.total_cost:.2f} |", "", "## Service-time sensitivity", ""]
    for row in sensitivity:
        lines.append(f"- {row['multiplier']}× service time: threshold {row['threshold']:.2f}, breach rate {row['breach_rate']:.1%}, total cost ${row['total_cost']:.2f}")
    lines += ["", "> Synthetic data and assumed costs demonstrate the decision method; they do not establish production performance."]
    return "\n".join(lines) + "\n"
