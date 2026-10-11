# Synthetic data

`queuecal.data.synthetic_receipts` deterministically generates receipt-like merchant, date, and total fields. Each row includes a deliberately miscalibrated confidence, a frozen correctness label, explicit error cost, arrival time, review duration, and priority.

The seed is fixed. No receipt image, customer data, or external dataset is bundled. This keeps the demo reproducible while making clear that its results are not a benchmark on SROIE, CORD, or production traffic.
