from __future__ import annotations

from .models import FieldPrediction


def review_queue(rows: list[FieldPrediction], threshold: float) -> list[dict]:
    queued = [row for row in rows if row.confidence < threshold]
    queued.sort(key=lambda row: (-row.priority, row.arrival_minute, row.item_id, row.field))
    return [
        {"item_id": row.item_id, "field": row.field, "confidence": round(row.confidence, 4), "priority": row.priority, "error_cost": row.error_cost}
        for row in queued
    ]
