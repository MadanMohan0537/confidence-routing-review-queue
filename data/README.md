# Synthetic data

`queuecal.data.synthetic_receipts` deterministically generates receipt-like merchant, date, and total fields. Each row includes a deliberately miscalibrated confidence, a frozen correctness label, explicit error cost, arrival time, review duration, and priority.

The seed is fixed. No receipt image, customer data, or external dataset is bundled. This keeps the demo reproducible while making clear that its results are not a benchmark on SROIE, CORD, or production traffic.

`queuecal.consistency.synthetic_amount_receipts` is a second frozen fixture with
12 subtotal/tax/total groups. Four totals contain a $2.50 inconsistency at high
confidence; two correct documents contain a low-confidence subtotal. The fixture
exists to compare independent routing with group routing, not to represent the
distribution of real receipt arithmetic.

