# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import subprocess
import sys
from pathlib import Path


def run_tests(input_file):
    """Run tests listed in a file.
    Lines starting with # or ; are ignored.

    :param input_file: Path to a file containing a list of tests to run.
    :type input_file: str
    """
    tests_to_run = []
    with open(input_file, "r") as f:
        for line in f:
            if len(line) < 1 or line[0] in ["#", ";"]:
                continue
            if "[" in line:
                line = line.split("[")[0]
            line = line.strip()
            if line not in tests_to_run:
                tests_to_run.append(line)
    for test_name in tests_to_run:
        print(test_name)

    for test_name in tests_to_run:
        print(f"Running test: {test_name}")
        subprocess.call(
            [
                sys.executable,
                "-m",
                "pytest",
                "--disable-warnings",
                "--disable-pytest-warnings",
                test_name,
            ],
            cwd=Path(__file__).parent.parent,
        )


if __name__ == "__main__":
    run_tests(sys.argv[1])
