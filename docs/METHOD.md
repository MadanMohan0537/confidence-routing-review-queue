# Method and limitations

QueueCal treats the threshold as an operations decision. A field is auto-approved when calibrated confidence is at least the threshold; otherwise it enters a priority review queue. The threshold curve reports automation, observed auto-approved errors, explicit error cost, reviewer hours, and combined cost.

The P1 simulator assigns arrivals to the earliest available reviewer and records wait-time SLA breaches. Its experiment compares the economic-only threshold with a threshold selected under a five-percent breach constraint during a three-times arrival-rate surge. When no candidate is feasible, the simulator explicitly chooses the least-bad breach rate rather than silently optimizing cost. Service time is swept from 0.75× to 1.5× because this assumption can dominate the result.

The P2 experiment evaluates document-level dependencies separately from confidence. For each complete subtotal, tax, and total group, QueueCal checks whether `abs(subtotal + tax - total) > 0.02`. A failure adds the entire three-field group to review, unioned with ordinary low-confidence routing. The frozen fixture has 12 documents, four high-confidence bad totals, and two unrelated low-confidence fields. Acceptance was declared before running the fixture: catch all four bad totals, flag no correct document, and add at most three field reviews per additional caught error.

The delayed-label audit joins correction events to immutable `item:field`
decision IDs and rejects duplicate, unknown, or invalid events. At each declared
window it records labels received over decisions, errors observed over eventual
errors, the threshold selected from visible labels, and that policy's cost on
eventual full truth. Regret is the latter cost minus the oracle full-truth cost.
With no visible labels the audit returns `INSUFFICIENT_LABELS` and does not
manufacture a threshold or regret value.

Limitations:

- The data, confidence scores, costs, arrivals, and reviewer times are synthetic.
- Histogram calibration on the same fixture is illustrative and optimistic; production work needs held-out or cross-validated calibration.
- The delayed-label fixture has eventual truth, while production systems rarely do; real regret remains unidentified until labels arrive.
- Correction observation is selective. Reporting coverage exposes the gap but does not statistically repair selection bias.
- The queue is deterministic and ignores breaks, skills, abandonment, and correlated document handling.
- The amount rule covers one currency and assumes taxes are represented additively; discounts, tips, multiple tax lines, OCR normalization, and currency conversion are out of scope.
- A consistency failure localizes a document group, not the erroneous field. Human review remains required.
- Error and review costs are explicit assumptions, not measured business values.
- A feasible simulated threshold is not evidence that automation is safe in a regulated workflow.

