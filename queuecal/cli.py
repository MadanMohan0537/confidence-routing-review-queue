from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .demo import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QueueCal's calibrated routing simulation")
    parser.add_argument("--json", default="queuecal-report.json")
    parser.add_argument("--markdown", default="queuecal-report.md")
    args = parser.parse_args()
    report = run_demo()
    markdown = report.pop("markdown")
    serializable = {**report, "baseline": asdict(report["baseline"]), "capacity_aware": asdict(report["capacity_aware"])}
    with open(args.json, "w", encoding="utf-8") as handle:
        json.dump(serializable, handle, indent=2, sort_keys=True)
    with open(args.markdown, "w", encoding="utf-8") as handle:
        handle.write(markdown)
    print(json.dumps({k: v for k, v in serializable.items() if k != "queue_preview"}, indent=2))


if __name__ == "__main__":
    main()
