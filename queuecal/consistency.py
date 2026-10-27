from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


AMOUNT_FIELDS = ("subtotal", "tax", "total")


@dataclass(frozen=True)
class AmountPrediction:
    item_id: str
    field: str
    value: float
    confidence: float
    correct: bool
    error_cost: float
    review_minutes: float = 2.0


@dataclass(frozen=True)
class ConsistencyComparison:
    documents: int
    seeded_inconsistent_documents: int
    baseline_reviewed_fields: int
    grouped_reviewed_fields: int
    baseline_caught_errors: int
    grouped_caught_errors: int
    additional_errors_caught: int
    extra_field_reviews: int
    added_reviews_per_caught_error: float | None
    false_positive_group_reviews: int
    acceptance_passed: bool


def synthetic_amount_receipts() -> list[AmountPrediction]:
    """Frozen amount fixture with four high-confidence arithmetic failures."""
    rows: list[AmountPrediction] = []
    for index in range(12):
        subtotal = 40.0 + index * 3.0
        tax = round(subtotal * 0.1, 2)
        total = round(subtotal + tax, 2)
        inconsistent = index in {1, 4, 7, 10}
        if inconsistent:
            total += 2.50
        values = {"subtotal": subtotal, "tax": tax, "total": total}
        for field in AMOUNT_FIELDS:
            low_confidence = index in {2, 8} and field == "subtotal"
            rows.append(
                AmountPrediction(
                    item_id=f"amount-receipt-{index:03d}",
                    field=field,
                    value=values[field],
                    confidence=0.64 if low_confidence else 0.93,
                    correct=not (inconsistent and field == "total"),
                    error_cost=80.0 if field == "total" else 20.0,
                )
            )
    return rows


def group_by_document(rows: list[AmountPrediction]) -> dict[str, dict[str, AmountPrediction]]:
    documents: dict[str, dict[str, AmountPrediction]] = {}
    for row in rows:
        if row.field not in AMOUNT_FIELDS:
            raise ValueError(f"unsupported amount field: {row.field}")
        if not isfinite(row.value) or not 0 <= row.confidence <= 1:
            raise ValueError("amounts must be finite and confidence must be in [0, 1]")
        fields = documents.setdefault(row.item_id, {})
        if row.field in fields:
            raise ValueError(f"duplicate {row.field} for {row.item_id}")
        fields[row.field] = row
    for item_id, fields in documents.items():
        missing = set(AMOUNT_FIELDS) - fields.keys()
        if missing:
            raise ValueError(f"{item_id} missing fields: {sorted(missing)}")
    return documents


def inconsistent_documents(
    rows: list[AmountPrediction], *, absolute_tolerance: float = 0.02
) -> set[str]:
    if absolute_tolerance < 0:
        raise ValueError("absolute_tolerance must be non-negative")
    documents = group_by_document(rows)
    return {
        item_id
        for item_id, fields in documents.items()
        if abs(fields["subtotal"].value + fields["tax"].value - fields["total"].value)
        > absolute_tolerance
    }


def review_ids(
    rows: list[AmountPrediction],
    threshold: float,
    *,
    grouped: bool,
    absolute_tolerance: float = 0.02,
) -> set[tuple[str, str]]:
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1]")
    selected = {(row.item_id, row.field) for row in rows if row.confidence < threshold}
    if grouped:
        flagged = inconsistent_documents(rows, absolute_tolerance=absolute_tolerance)
        selected.update((row.item_id, row.field) for row in rows if row.item_id in flagged)
    return selected


def compare_correlated_review(
    rows: list[AmountPrediction],
    threshold: float = 0.80,
    *,
    absolute_tolerance: float = 0.02,
    max_added_reviews_per_caught_error: float = 3.0,
) -> ConsistencyComparison:
    documents = group_by_document(rows)
    flagged = inconsistent_documents(rows, absolute_tolerance=absolute_tolerance)
    baseline_ids = review_ids(rows, threshold, grouped=False)
    grouped_ids = review_ids(
        rows, threshold, grouped=True, absolute_tolerance=absolute_tolerance
    )
    incorrect = {(row.item_id, row.field) for row in rows if not row.correct}
    baseline_caught = len(incorrect & baseline_ids)
    grouped_caught = len(incorrect & grouped_ids)
    additional_caught = grouped_caught - baseline_caught
    extra_reviews = len(grouped_ids - baseline_ids)
    ratio = extra_reviews / additional_caught if additional_caught else None
    false_positives = sum(
        1
        for item_id in flagged
        if all(row.correct for row in documents[item_id].values())
    )
    passed = (
        grouped_caught == len(incorrect)
        and additional_caught > 0
        and false_positives == 0
        and ratio is not None
        and ratio <= max_added_reviews_per_caught_error
    )
    return ConsistencyComparison(
        documents=len(documents),
        seeded_inconsistent_documents=len(
            {row.item_id for row in rows if not row.correct}
        ),
        baseline_reviewed_fields=len(baseline_ids),
        grouped_reviewed_fields=len(grouped_ids),
        baseline_caught_errors=baseline_caught,
        grouped_caught_errors=grouped_caught,
        additional_errors_caught=additional_caught,
        extra_field_reviews=extra_reviews,
        added_reviews_per_caught_error=ratio,
        false_positive_group_reviews=false_positives,
        acceptance_passed=passed,
    )
