# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import dotenv


def normalize_test_name(test_name):
    if "[" in test_name:
        test_name = test_name.split("[")[0]
    return test_name.strip()


def extract_test_location(location):
    test_path, line_no, test_func = location
    test_class_name, test_func_name = test_func.split(".", 1)
    test_class = test_path.split(os.path.sep, 3)[-1] + "::" + test_class_name
    m = re.match(r"(\w+)\[(\w+)]", test_func_name)
    if m:
        test_func_name, test_param = m.groups()
    else:
        test_param = None
    return test_class, test_func_name, test_param


def load_tests_from_file(input_file):
    tests_to_run = set()
    with open(input_file, "r") as f:

        for line in f:
            if len(line) < 1 or line[0] in ["#", ";"]:
                continue
            line = normalize_test_name(line)
            tests_to_run.add(line)
    return tests_to_run


@contextlib.contextmanager
def update_dot_env_file(env_override):
    """Update env file with env_override, and restore it after the context is exited.
    Support bool variable only for now.
    """
    env_file = dotenv.find_dotenv(raise_error_if_not_found=True)
    print(f"Updating env file: {env_file}")
    origin_env_content = None
    try:
        with open(env_file, "r") as f:
            origin_env_content = f.read()
            env_vars = [line.strip() for line in origin_env_content.splitlines() if line.strip()]
        for key, value in env_override.items():
            if isinstance(value, bool):
                target_line = f"{key}='true'"
                for i, line in enumerate(env_vars):
                    if line == target_line and not value:
                        env_vars[i] = f"#{target_line}"
                    elif re.match(rf"# *{target_line}", line) and value:
                        env_vars[i] = f"{target_line}"
        with open(env_file, "w") as f:
            f.write("\n".join(env_vars))
        yield
    finally:
        if origin_env_content is not None:
            with open(env_file, "w") as f:
                f.write(origin_env_content)


def run_simple(tests_to_run, working_dir, extra_params, is_live_and_recording):
    print(f"Running {len(tests_to_run)} tests under {working_dir}: ")
    for test_name in tests_to_run:
        print(test_name)

    with update_dot_env_file(
        {"AZURE_TEST_RUN_LIVE": is_live_and_recording, "AZURE_SKIP_LIVE_RECORDING": not is_live_and_recording},
    ):
        for test_name in tests_to_run:
            print(
                f"pytest {test_name} {' '.join(extra_params)} in {'live' if is_live_and_recording else 'playback'} mode..."
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    test_name,
                ]
                + extra_params,
                cwd=working_dir,
            )


def run_tests(tests_to_run, extras, *, skip_first_run=False, record_mismatch=False, is_live_and_recording=False):
    working_dir = Path(__file__).parent.parent
    if record_mismatch:
        log_file_path = working_dir / "scripts" / "tmp" / "pytest_log.json"
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        if not skip_first_run:
            run_simple(
                tests_to_run,
                working_dir,
                extra_params=[
                    "--disable-warnings",
                    "--disable-pytest-warnings",
                    "--report-log",
                    log_file_path.as_posix(),
                ]
                + extras,
                is_live_and_recording=False,
            )

        tests_failed_with_recording_mismatch = defaultdict(dict)
        with open(log_file_path, "r") as f:
            for line in f:
                node = json.loads(line)
                if "outcome" not in node:
                    continue
                if node["outcome"] != "failed":
                    continue
                test_class, test_name, test_param = extract_test_location(node["location"])

                msg = node["longrepr"]["reprcrash"]["message"]
                if "ResourceNotFoundError" in msg:
                    if test_param is None:
                        tests_failed_with_recording_mismatch[test_class][test_name] = None
                    elif test_name not in tests_failed_with_recording_mismatch[test_class]:
                        tests_failed_with_recording_mismatch[test_class][test_name] = [test_param]
                    else:
                        tests_failed_with_recording_mismatch[test_class][test_name].append(test_param)

        if tests_failed_with_recording_mismatch:
            # re-run the tests with recording mismatch in live mode
            for test_class, test_info in tests_failed_with_recording_mismatch.items():
                keys = []
                for test_name, test_params in test_info.items():
                    if test_params is not None:
                        keys.append(f"{test_name}[{'-'.join(test_params)}]")
                    else:
                        keys.append(test_name)
                run_simple(
                    [test_class],
                    working_dir,
                    ["-k", " or ".join(keys), "--tb=line"],
                    is_live_and_recording=True,
                )

            # re-run the original tests to check if they are still failing
            run_simple(tests_to_run, working_dir, extras, is_live_and_recording=False)
    else:
        run_simple(tests_to_run, working_dir, extras, is_live_and_recording=is_live_and_recording)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        type=str,
        help="File containing tests to run, each line is a test name",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Name of the test to run. Format is aligned with pytest, e.g. 'tests/pipeline_job/'.",
    )
    parser.add_argument(
        "--record-mismatch",
        "-r",
        action="store_true",
        help="If specified, pytest log will be outputted to tmp/pytest_log.json, "
        "then tests failed with recording not found error will be rerun in live & recording mode."
        "Note that .env file will be updated during the process, so please revert the change manually "
        "if the script run is stopped early.",
    )
    parser.add_argument(
        "--skip-first-run",
        "-s",
        action="store_true",
        help="If specified, will skip the first run in record-mismatch mode.",
    )

    _args, _extras = parser.parse_known_args()

    if _args.file:
        _tests = load_tests_from_file(_args.file)
    elif _args.name:
        _tests = [_args.name]
    else:
        raise ValueError("Must specify either --file or --name")
    run_tests(
        _tests,
        _extras,
        skip_first_run=_args.skip_first_run,
        record_mismatch=_args.record_mismatch,
    )
