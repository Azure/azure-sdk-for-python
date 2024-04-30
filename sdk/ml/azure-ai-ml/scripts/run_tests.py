# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
import contextlib
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import dotenv

# pylint: disable=consider-using-with


def normalize_test_name(test_name):
    if "[" in test_name:
        test_name = test_name.split("[")[0]
    return test_name.strip()


def location_to_test_name(location):
    test_path, _, test_func = location
    test_class_name, test_func_name = test_func.split(".", 1)
    test_class = test_path.split(os.path.sep, 3)[-1] + "::" + test_class_name
    return test_class + "::" + test_func_name


def extract_test_location(test_name):
    splitor_num = test_name.count("::")
    if splitor_num <= 1:
        return test_name, None, None
    if splitor_num == 2:
        test_class, test_func_name = test_name.rsplit("::", 1)
        m = re.match(r"(\w+)\[(\w+)]", test_func_name)
        if m:
            test_func_name, test_param = m.groups()
        else:
            test_param = None
        return test_class, test_func_name, test_param
    raise ValueError(f"Invalid test name: {test_name}")


def load_tests_from_file(input_file):
    tests_to_run = set()
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if len(line) < 1 or line[0] in ["#", ";"]:
                continue
            tests_to_run.add(line.strip())
    return tests_to_run


@contextlib.contextmanager
def update_dot_env_file(env_override):
    """Update env file with env_override, and restore it after the context is exited.
    Support bool variable only for now.

    :param: env_override
    :type: dict
    :return: None
    """
    env_file = dotenv.find_dotenv(raise_error_if_not_found=True)
    print(f"Updating env file: {env_file}")
    origin_env_content = None
    try:
        with open(env_file, "r", encoding="utf-8") as f:
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
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("\n".join(env_vars))
        yield
    finally:
        if origin_env_content is not None:
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(origin_env_content)


def run_simple(
    tests_to_run,
    working_dir,
    extra_params,
    *,
    is_live_and_recording,
    log_file_path,
    log_suffix=None,
    log_in_json=False,
):
    print(f"Running {len(tests_to_run)} tests under {working_dir}: ")
    for test_name in tests_to_run:
        print(test_name)

    if log_file_path and log_suffix:
        log_file_path = log_file_path.with_suffix(log_file_path.suffix + log_suffix)

    if log_in_json:
        if log_file_path is None:
            raise ValueError("log_file_path must be specified when log_in_json is True")
        stdout = None
        json_log_file_path = log_file_path.with_suffix(log_file_path.suffix + ".log")
    else:
        stdout = open(log_file_path.with_suffix(log_file_path.suffix + ".txt"), "w", encoding="utf-8")
        json_log_file_path = None

    with update_dot_env_file(
        {"AZURE_TEST_RUN_LIVE": is_live_and_recording, "AZURE_SKIP_LIVE_RECORDING": not is_live_and_recording},
    ):
        for test_class, keyword_param in reorganize_tests(tests_to_run):
            tmp_extra_params = extra_params + keyword_param
            if log_in_json:
                # use a temp json file to avoid overwriting the final log file
                temp_log_file_path = json_log_file_path.with_stem("temp")
                tmp_extra_params += ["--report-log", temp_log_file_path.as_posix()]

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    test_class,
                ]
                + tmp_extra_params,
                cwd=working_dir,
                stdout=stdout,
                check=False,
            )
            if log_in_json:
                # append temp json file to the final log file
                with open(json_log_file_path, "a", encoding="utf-8") as f:
                    f.write(temp_log_file_path.read_text())
    if stdout is not None:
        stdout.close()
        print(log_file_path.with_suffix(log_file_path.suffix + ".txt").read_text())

    return json_log_file_path


def reorganize_tests(tests_to_run):
    reorganized_tests = {}
    for test_name in tests_to_run:
        test_class, test_func_name, test_param = extract_test_location(test_name)

        if test_func_name is None:
            # Register all tests in test_class
            reorganized_tests[test_class] = None
            continue
        if test_class not in reorganized_tests:
            reorganized_tests[test_class] = {}
        if reorganized_tests[test_class] is None:
            # All tests in test_class have been registered
            continue

        if test_param is None:
            # Register all params for test_class::test_func_name
            reorganized_tests[test_class][test_func_name] = None
            continue
        if test_func_name not in reorganized_tests[test_class]:
            reorganized_tests[test_class][test_func_name] = []
        if reorganized_tests[test_class][test_func_name] is None:
            # All params for test_class::test_func_name have been registered
            continue

        reorganized_tests[test_class][test_func_name].append(test_param)

    # re-run the tests with recording mismatch in live mode
    for test_class, test_info in reorganized_tests.items():
        if test_info is None:
            yield test_class, []
            continue
        keys = []
        for test_func_name, test_params in test_info.items():
            if test_params is not None:
                # TODO: problem in using parametrize with pytest-xdist
                # keys.append(f"{test_func_name}[{'-'.join(test_params)}]")
                keys.append(f"{test_func_name}")
            else:
                keys.append(test_func_name)
        keyword_param = ["-k", " or ".join(keys)]
        yield test_class, keyword_param


def get_base_log_path(working_dir, *, create_new=True):
    log_dir = working_dir / "scripts" / "tmp"
    if not create_new:
        logs = sorted(glob.glob(str(log_dir / "pytest.*.first.log")))
        if len(logs) == 0:
            raise RuntimeError("No previous run log file found")
        return Path(logs[-1][: -len(".first.log")])
    log_file_path = log_dir / "pytest.{}".format(datetime.now().strftime("%Y%m%d%H%M%S"))
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    return log_file_path


def get_failed_tests(log_file_path):
    tests_failed_with_recording_mismatch = []
    failed_tests = []
    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            node = json.loads(line)
            if "outcome" not in node:
                continue
            if node["outcome"] != "failed":
                continue
            test_name = location_to_test_name(node["location"])
            failed_tests.append(test_name)
            msg = node["longrepr"]["reprcrash"]["message"]
            if "NotFound" in msg:
                tests_failed_with_recording_mismatch.append(test_name)
    return failed_tests, tests_failed_with_recording_mismatch


def run_tests(args, extras):
    if args.file:
        tests_to_run = load_tests_from_file(args.file)
    elif args.name:
        tests_to_run = [args.name]
    elif args.skip_first_run and args.record_mismatch:
        # load failed tests from last run log
        tests_to_run = []
    else:
        raise ValueError("Must specify either --file or --name")
    skip_first_run = args.skip_first_run
    record_mismatch = args.record_mismatch

    working_dir = Path(__file__).parent.parent
    log_file_path = get_base_log_path(working_dir, create_new=not skip_first_run)

    if skip_first_run:
        json_log_file_path = log_file_path.with_suffix(log_file_path.suffix + ".first.log")
    else:
        json_log_file_path = run_simple(
            tests_to_run,
            working_dir,
            extras + ["--disable-warnings", "--disable-pytest-warnings"],
            # first run is always in playback mode
            is_live_and_recording=False,
            log_file_path=log_file_path,
            log_in_json=True,
            log_suffix=".first",
        )

    failed_tests, tests_failed_with_recording_mismatch = get_failed_tests(json_log_file_path)
    failed_tests_path = log_file_path.with_suffix(log_file_path.suffix + ".failed.txt")
    with open(failed_tests_path, "w", encoding="utf-8") as f:
        f.write("\n".join(failed_tests))

    if record_mismatch and tests_failed_with_recording_mismatch:
        print(f"Redo live mode recording for tests: {failed_tests_path}")
        run_simple(
            tests_failed_with_recording_mismatch,
            working_dir,
            extra_params=["--tb=line"],
            is_live_and_recording=True,
            log_suffix=".record",
            log_file_path=log_file_path,
        )

        print(f"Rerun playback mode for failed tests: {failed_tests_path}")
        run_simple(
            failed_tests,
            working_dir,
            extra_params=extras + ["--disable-warnings", "--disable-pytest-warnings"],
            is_live_and_recording=False,
            log_file_path=log_file_path,
            log_suffix=".final",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="File containing tests to run, each line is a test name",
    )
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        help="Name of the test to run. Usual pytest formats are supported, e.g., 'tests/pipeline_job/' "
        "and 'tests/pipeline_job/e2etests/test_pipeline_job.py::TestPipelineJob'."
        "Test param specification is also supported, e.g., 'tests/pipeline_job/e2etests/"
        "test_pipeline_job.py::TestPipelineJob::test_pipeline_job_with_data_binding_expression[0-input_basic.yml]'",
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
        help="If specified, will skip the first run in record-mismatch mode. Failed tests will be loaded from "
        "tmp/pytest_first_run.log generated in previous record-mismatch mode first run.",
    )

    _args, _extras = parser.parse_known_args()

    run_tests(
        _args,
        _extras,
    )
