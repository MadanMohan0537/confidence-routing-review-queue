# Evidence-driven backlog

| Priority | Feature | User problem and behavior | Dependencies | Success test | Risks and tradeoffs | Status |
|---|---|---|---|---|---|---|
| P1 | Capacity-aware routing | A safe threshold overloads the review queue. Simulate arrivals, service times, reviewers, priorities, and SLAs; choose among candidate thresholds. | Calibrated scores, cost table, queue simulator | Under a frozen traffic surge, reduce SLA breaches without increasing total error cost beyond the declared budget; record denominators and service-time sensitivity | Service assumptions dominate; sweep 0.75×–1.5× | Shipped |
| P2 | Correlated field review | Independent thresholds miss subtotal/tax/total contradictions. Route the field group when consistency rules fail. | Document grouping, arithmetic rules | Catch every seeded inconsistency and report extra reviews per caught error | Over-grouping increases workload; current MVP handles one additive rule and one currency | Shipped |
| P2 | Delayed-label audit | Auto-approved mistakes surface days later and escape calibration. Join delayed corrections to original decisions. | Stable IDs, label windows | Recover seeded delayed errors and quantify threshold regret | Labels may be selectively observed | Planned |
| P2 | Reviewer behavior monitor | Rubber-stamping corrupts feedback. Insert known-bad controls and measure reviewer-specific agreement. | Review identity, gold controls | Detect seeded rubber-stamping with a predeclared false-alert bound | Surveillance concerns; aggregate where possible | Planned |
| P2 | Cost uncertainty bands | A single error-cost table creates false precision. Sweep bounded business-owned costs. | Scenario inputs | Recommended region stays stable or uncertainty is surfaced | Wider ranges may prevent a single answer | Planned |
| P3 | Per-field thresholds | Total errors cost more than merchant formatting errors. Optimize thresholds by field under one capacity budget. | Field labels, constrained search | Lower total cost at equal SLA breach rate than global threshold | Harder to explain and maintain | Planned |
| P3 | Fairness and access slices | Queue latency may vary by document type or language. Report service and error metrics by declared slices. | Ethical slice definitions, enough samples | Detect seeded disparity with intervals and minimum denominators | Small slices create noise and privacy risk | Planned |
| P3 | Arrival-regime detection | Static forecasts fail during seasonality. Detect regime shifts and recommend safe fallback. | Time series, change detector | Trigger before seeded queue instability with bounded false alarms | Reactive threshold changes can oscillate | Planned |
| P4 | Active-review allocation | Review scarce cases that improve calibration most. Rank by decision value, not uncertainty alone. | Online calibration, value model | Better held-out cost after equal review budget | Feedback loops may distort data | Planned |

## Further rigorous additions

| Priority | Feature | User problem and behavior | Dependencies | Success test | Risks and tradeoffs | Status |
|---|---|---|---|---|---|---|
| P2 | Rule attribution and correction capture | Reviewers see a group failure but not the likely cause. Rank suspect fields and record the corrected value without auto-editing. | Rule evidence, review outcomes, immutable decision IDs | On a held-out synthetic set, top-two attribution contains the corrected field at least 90% of the time; report misses | Attribution may anchor reviewers; show rule evidence and permit override | Planned |
| P2 | Compound receipt arithmetic | Tips, discounts, multiple tax lines, and rounding produce false alerts under one additive rule. Represent signed components and currency-specific tolerances. | Normalized amount schema, currency metadata | Reduce false group reviews on a frozen compound fixture without missing seeded contradictions | More permissive rules can hide errors; retain per-rule recall | Planned |
| P2 | Group-aware queue cost | Three linked fields may take less time than three independent reviews. Simulate document setup cost plus marginal field cost. | Review timing observations, queue simulator | Capacity forecast error falls on held-out synthetic service traces | Synthetic timing assumptions can create false precision | Planned |

Next slice: delayed-label audit, because calibration and threshold regret are currently computed as if correctness were immediate and fully observed.

