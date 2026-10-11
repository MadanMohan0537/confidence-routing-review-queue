from __future__ import annotations

import random

from .models import FieldPrediction


FIELDS = (("merchant", 8.0), ("date", 15.0), ("total", 80.0))


def synthetic_receipts(count: int = 60, seed: int = 17, arrival_scale: float = 1.0) -> list[FieldPrediction]:
    """Frozen, reproducible receipt-like predictions with known labels."""
    rng = random.Random(seed)
    rows: list[FieldPrediction] = []
    minute = 0.0
    for item in range(count):
        minute += rng.uniform(0.7, 2.2) / arrival_scale
        difficulty = rng.random()
        for field, error_cost in FIELDS:
            raw = max(0.03, min(0.99, 0.97 - 0.62 * difficulty + rng.uniform(-0.12, 0.12)))
            # Deliberately overconfident synthetic model.
            actual_probability = max(0.02, min(0.98, raw - 0.10 - (0.08 if field == "total" else 0)))
            correct = rng.random() < actual_probability
            rows.append(FieldPrediction(
                f"receipt-{item:03d}", field, raw, correct, error_cost, minute,
                2.0 + (2.0 if field == "total" else 0.5), 3 if field == "total" else 1,
            ))
    return rows
