# Method and limitations

QueueCal treats the threshold as an operations decision. A field is auto-approved when calibrated confidence is at least the threshold; otherwise it enters a priority review queue. The threshold curve reports automation, observed auto-approved errors, explicit error cost, reviewer hours, and combined cost.

The P1 simulator assigns arrivals to the earliest available reviewer and records wait-time SLA breaches. Its experiment compares the economic-only threshold with a threshold selected under a five-percent breach constraint during a three-times arrival-rate surge. When no candidate is feasible, the simulator explicitly chooses the least-bad breach rate rather than silently optimizing cost. Service time is swept from 0.75× to 1.5× because this assumption can dominate the result.

Limitations:

- The data, confidence scores, costs, arrivals, and reviewer times are synthetic.
- Histogram calibration on the same fixture is illustrative and optimistic; production work needs held-out or cross-validated calibration.
- Observed correctness is treated as immediate and complete; delayed labels are planned.
- The queue is deterministic and ignores breaks, skills, abandonment, and correlated document handling.
- Error and review costs are explicit assumptions, not measured business values.
- A feasible simulated threshold is not evidence that automation is safe in a regulated workflow.
