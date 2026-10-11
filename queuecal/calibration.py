from __future__ import annotations

from .models import CalibrationBin, FieldPrediction


def calibration_bins(rows: list[FieldPrediction], bins: int = 5) -> list[CalibrationBin]:
    result: list[CalibrationBin] = []
    for index in range(bins):
        lower, upper = index / bins, (index + 1) / bins
        members = [r for r in rows if lower <= r.confidence <= upper if index == bins - 1 or r.confidence < upper]
        if members:
            result.append(CalibrationBin(lower, upper, len(members), sum(r.confidence for r in members) / len(members), sum(r.correct for r in members) / len(members)))
    return result


def expected_calibration_error(rows: list[FieldPrediction], bins: int = 5) -> float:
    groups = calibration_bins(rows, bins)
    return sum(group.count / len(rows) * abs(group.mean_confidence - group.accuracy) for group in groups)


def calibrate(rows: list[FieldPrediction], bins: int = 5) -> list[FieldPrediction]:
    groups = calibration_bins(rows, bins)
    calibrated: list[FieldPrediction] = []
    for row in rows:
        group = next(group for group in groups if group.lower <= row.confidence <= group.upper and (row.confidence < group.upper or group.upper == 1.0))
        calibrated.append(FieldPrediction(**{**row.__dict__, "confidence": group.accuracy}))
    return calibrated
