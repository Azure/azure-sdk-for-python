# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Self-contained script used as a Code Interpreter upload payload by
`sample_agent_run_uploaded_script.py`. Pure Python standard library only,
so it can run inside the sandboxed Code Interpreter container without
network access or extra dependencies.
"""

import statistics
from datetime import date


def main() -> None:
    quarterly_revenue = {
        "Q1": 1_240_500,
        "Q2": 1_375_200,
        "Q3": 1_188_900,
        "Q4": 1_502_800,
    }

    total = sum(quarterly_revenue.values())
    mean = statistics.mean(quarterly_revenue.values())
    median = statistics.median(quarterly_revenue.values())
    stdev = statistics.stdev(quarterly_revenue.values())
    best_quarter = max(quarterly_revenue, key=quarterly_revenue.get)

    print(f"Report generated: {date.today().isoformat()}")
    print("Quarterly revenue:")
    for q, v in quarterly_revenue.items():
        print(f"  {q}: ${v:,}")
    print()
    print(f"Total:        ${total:,}")
    print(f"Mean:         ${mean:,.2f}")
    print(f"Median:       ${median:,.2f}")
    print(f"Std dev:      ${stdev:,.2f}")
    print(f"Best quarter: {best_quarter} (${quarterly_revenue[best_quarter]:,})")


if __name__ == "__main__":
    main()
