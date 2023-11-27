import sys
import os
import shutil
import re
import multiprocessing
import glob

from typing import List
from argparse import Namespace

from common_tasks import (
    run_check_call,
    clean_coverage,
    is_error_code_5_allowed,
    create_code_coverage_params,
)

from ci_tools.variables import in_ci
from ci_tools.environment_exclusions import filter_tox_environment_string
from ci_tools.ci_interactions import output_ci_warning
from ci_tools.scenario.generation import replace_dev_reqs
from ci_tools.functions import cleanup_directory
from pkg_resources import parse_requirements, RequirementParseError
import logging

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
coverage_dir = os.path.join(root_dir, "_coverage/")
pool_size = multiprocessing.cpu_count() * 2
DEFAULT_TOX_INI_LOCATION = os.path.join(root_dir, "eng/tox/tox.ini")
IGNORED_TOX_INIS = ["azure-cosmos"]
test_tools_path = os.path.join(root_dir, "eng", "test_tools.txt")
dependency_tools_path = os.path.join(root_dir, "eng", "dependency_tools.txt")


def combine_coverage_files(targeted_packages):
    # find tox.ini file. tox.ini is used to combine coverage paths to generate formatted report
    tox_ini_file = os.path.join(root_dir, "eng", "tox", "tox.ini")
    config_file_flag = "--rcfile={}".format(tox_ini_file)

    if os.path.isfile(tox_ini_file):
        # for every individual coverage file, run coverage combine to combine path
        for package_dir in [package for package in targeted_packages]:
            coverage_file = os.path.join(package_dir, ".coverage")
            if os.path.isfile(coverage_file):
                cov_cmd_array = [sys.executable, "-m", "coverage", "combine"]
                # tox.ini file has coverage paths to combine
                # Pas tox.ini as coverage config file
                cov_cmd_array.extend([config_file_flag, coverage_file])
                run_check_call(cov_cmd_array, package_dir)
    else:
        # not a hard error at this point
        # this combine step is required only for modules if report has package name starts with .tox
        logging.error("tox.ini is not found in path {}".format(root_dir))


def collect_tox_coverage_files(targeted_packages):
    root_coverage_dir = os.path.join(root_dir, "_coverage/")

    clean_coverage(coverage_dir)

    # coverage combine fixes this with the help of tox.ini[coverage:paths]
    coverage_files = []
    for package_dir in [package for package in targeted_packages]:
        coverage_file = os.path.join(package_dir, ".coverage")
        if os.path.isfile(coverage_file):
            destination_file = os.path.join(root_coverage_dir, ".coverage_{}".format(os.path.basename(package_dir)))
            shutil.copyfile(coverage_file, destination_file)
            coverage_files.append(destination_file)

    logging.info("Uploading .coverage files: {}".format(coverage_files))


def compare_req_to_injected_reqs(parsed_req, injected_packages):
    if parsed_req is None:
        return False

    return any(parsed_req.name in req for req in injected_packages)


def inject_custom_reqs(file, injected_packages, package_dir):
    req_lines = []
    injected_packages = [p for p in re.split("[\s,]", injected_packages) if p]

    if injected_packages:
        logging.info("Adding custom packages to requirements for {}".format(package_dir))
        with open(file, "r") as f:
            for line in f:
                logging.info("Attempting to parse {}".format(line))
                try:
                    parsed_req = [req for req in parse_requirements(line)]
                except Exception as e:
                    logging.error(e)
                    parsed_req = [None]
                req_lines.append((line, parsed_req))

        if req_lines:
            all_adjustments = injected_packages + [
                line_tuple[0].strip()
                for line_tuple in req_lines
                if line_tuple[0].strip() and not compare_req_to_injected_reqs(line_tuple[1][0], injected_packages)
            ]
        else:
            all_adjustments = injected_packages

        logging.info("Generated Custom Reqs: {}".format(req_lines))

        with open(file, "w") as f:
            # note that we directly use '\n' here instead of os.linesep due to how f.write() actually handles this stuff internally
            # If a file is opened in text mode (the default), during write python will accidentally double replace due to "\r" being
            # replaced with "\r\n" on Windows. Result: "\r\n\n". Extra line breaks!
            f.write("\n".join(all_adjustments))


def collect_log_files(working_dir):
    logging.info("Collecting log files from {}".format(working_dir))
    package = working_dir.split("/")[-1]
    # collect all the log files into one place for publishing in case of tox failure

    log_directory = os.path.join(root_dir, "_tox_logs")

    try:
        os.mkdir(log_directory)
        logging.info("Created log directory: {}".format(log_directory))
    except OSError:
        logging.info("'{}' directory already exists".format(log_directory))

    log_directory = os.path.join(log_directory, package)

    try:
        os.mkdir(log_directory)
        logging.info("Created log directory: {}".format(log_directory))
    except OSError:
        logging.info("'{}' directory already exists".format(log_directory))

    log_directory = os.path.join(log_directory, sys.version.split()[0])

    try:
        os.mkdir(log_directory)
        logging.info("Created log directory: {}".format(log_directory))
    except OSError:
        logging.info("'{}' directory already exists".format(log_directory))

    for test_env in glob.glob(os.path.join(working_dir, ".tox", "*")):
        env = os.path.split(test_env)[-1]
        logging.info("env: {}".format(env))
        log_files = os.path.join(test_env, "log")

        if os.path.exists(log_files):
            logging.info("Copying log files from {} to {}".format(log_files, log_directory))

            temp_dir = os.path.join(log_directory, env)
            logging.info("TEMP DIR: {}".format(temp_dir))
            try:
                os.mkdir(temp_dir)
                logging.info("Created log directory: {}".format(temp_dir))
            except OSError:
                logging.info("Could not create '{}' directory".format(temp_dir))
                break

            for filename in os.listdir(log_files):
                if filename.endswith(".log"):
                    logging.info("LOG FILE: {}".format(filename))

                    file_location = os.path.join(log_files, filename)
                    shutil.move(file_location, os.path.join(temp_dir, filename))
                    logging.info("Moved file to {}".format(os.path.join(temp_dir, filename)))
        else:
            logging.info("Could not find {} directory".format(log_files))

    for f in glob.glob(os.path.join(root_dir, "_tox_logs", "*")):
        logging.info("Log file: {}".format(f))


def cleanup_tox_environments(tox_dir: str, command_array: str) -> None:
    """The new .coverage formats are no longer readily amended in place. Because we can't amend them in place,
    we can't amend the source location to remove the path ".tox/<envname>/site-packages/". Because of this, we will
    need the source where it was generated to stick around. We can do that by being a bit more circumspect about which
    files we actually delete/clean up!
    """
    if "--cov-append" in command_array:
        folders = [folder for folder in os.listdir(tox_dir) if "whl" != folder]
        for folder in folders:
            try:
                cleanup_directory(folder)
            except Exception as e:
                # git has a permissions problem. one of the files it drops
                # cannot be removed as no one has the permission to do so.
                # lets log just in case, but this should really only affect windows machines.
                logging.info(e)
                pass
    else:
        cleanup_directory(tox_dir)


def execute_tox_serial(tox_command_tuples):
    return_code = 0

    for index, cmd_tuple in enumerate(tox_command_tuples):
        tox_dir = os.path.abspath(os.path.join(cmd_tuple[1], "./.tox/"))
        clone_dir = os.path.abspath(os.path.join(cmd_tuple[1], "..", "..", "..", "l"))
        logging.info("tox_dir: {}".format(tox_dir))

        logging.info(
            "Running tox for {}. {} of {}.".format(os.path.basename(cmd_tuple[1]), index + 1, len(tox_command_tuples))
        )

        result = run_check_call(cmd_tuple[0], cmd_tuple[1], always_exit=False)

        if result is not None and result != 0:
            return_code = result

        if in_ci():
            collect_log_files(cmd_tuple[1])

            cleanup_tox_environments(tox_dir, cmd_tuple[0])

            if os.path.exists(clone_dir):
                try:
                    cleanup_directory(clone_dir)
                except Exception as e:
                    # git has a permissions problem. one of the files it drops
                    # cannot be removed as no one has the permission to do so.
                    # lets log just in case, but this should really only affect windows machines.
                    logging.info(e)
                    pass

    return return_code


def prep_and_run_tox(targeted_packages: List[str], parsed_args: Namespace) -> None:
    """
    Primary entry point for tox invocations during CI runs.

    :param targeted_packages: The set of targeted packages. These are not just package names, and are instead the full absolute path to the package root directory.
    :param parsed_args: An argparse namespace object from setup_execute_tests.py. Not including it will effectively disable "customizations"
        of the tox invocation.
    :param options_array: When invoking tox, these additional options will be passed to the underlying tox invocations as arguments.
        When invoking of "tox run -e whl -c ../../../eng/tox/tox.ini -- --suppress-no-test-exit-code", "--suppress-no-test-exit-code" the "--" will be
        passed directly to the pytest invocation.
    """
    options_array: List[str] = []
    if parsed_args.wheel_dir:
        os.environ["PREBUILT_WHEEL_DIR"] = parsed_args.wheel_dir

    if parsed_args.mark_arg:
        options_array.extend(["-m", "{}".format(parsed_args.mark_arg)])

    tox_command_tuples = []
    check_set = set([env.strip().lower() for env in parsed_args.tox_env.strip().split(",")])
    skipped_tox_checks = {}

    for index, package_dir in enumerate(targeted_packages):
        destination_tox_ini = os.path.join(package_dir, "tox.ini")
        destination_dev_req = os.path.join(package_dir, "dev_requirements.txt")

        tox_execution_array = [sys.executable, "-m", "tox"]

        if parsed_args.tenvparallel:
            tox_execution_array.extend(["run-parallel", "-p", "all"])
        else:
            tox_execution_array.append("run")

        # Tox command is run in package root, make tox set package root as {toxinidir}
        tox_execution_array += ["--root", "."]
        local_options_array = options_array[:]

        # Get code coverage params for current package
        package_name = os.path.basename(package_dir)
        coverage_commands = create_code_coverage_params(parsed_args, package_dir)
        local_options_array.extend(coverage_commands)

        pkg_egg_info_name = "{}.egg-info".format(package_name.replace("-", "_"))
        local_options_array.extend(["--ignore", pkg_egg_info_name])

        # if we are targeting only packages that are management plane, it is a possibility
        # that no tests running is an acceptable situation
        # we explicitly handle this here.
        if is_error_code_5_allowed(package_dir, package_name):
            local_options_array.append("--suppress-no-test-exit-code")

        # if not present, re-use base
        if not os.path.exists(destination_tox_ini) or (
            os.path.exists(destination_tox_ini) and os.path.basename(package_dir) in IGNORED_TOX_INIS
        ):
            logging.info(
                "No customized tox.ini present, using common eng/tox/tox.ini for {}".format(
                    os.path.basename(package_dir)
                )
            )
            tox_execution_array.extend(["-c", DEFAULT_TOX_INI_LOCATION])

        # handle empty file
        if not os.path.exists(destination_dev_req):
            logging.info("No dev_requirements present.")
            with open(destination_dev_req, "w+") as file:
                file.write("\n")

        if in_ci():
            replace_dev_reqs(destination_dev_req, package_dir)
            replace_dev_reqs(test_tools_path, package_dir)
            replace_dev_reqs(dependency_tools_path, package_dir)
            os.environ["TOX_PARALLEL_NO_SPINNER"] = "1"

        inject_custom_reqs(destination_dev_req, parsed_args.injected_packages, package_dir)

        if parsed_args.tox_env:
            filtered_tox_environment_set = filter_tox_environment_string(parsed_args.tox_env, package_dir)
            filtered_set = set([env.strip().lower() for env in filtered_tox_environment_set.strip().split(",")])

            if filtered_set != check_set:
                skipped_environments = check_set - filtered_set
                if in_ci() and skipped_environments:
                    for check in skipped_environments:
                        if check not in skipped_tox_checks:
                            skipped_tox_checks[check] = []

                    skipped_tox_checks[check].append(package_name)

            if not filtered_tox_environment_set:
                logging.info(
                    f'All requested tox environments "{parsed_args.tox_env}" for package {package_name} have been excluded as indicated by is_check_enabled().'
                    + " Check file /tools/azure-sdk-tools/ci_tools/environment_exclusions.py and the pyproject.toml."
                )

                continue

            tox_execution_array.extend(["-e", filtered_tox_environment_set])


        if parsed_args.tox_env == "apistub":
            local_options_array = []
            if parsed_args.dest_dir:
                local_options_array.extend(["--out-path", parsed_args.dest_dir])

        if local_options_array:
            tox_execution_array.extend(["--"] + local_options_array)

        tox_command_tuples.append((tox_execution_array, package_dir))

    if in_ci() and skipped_tox_checks:
        warning_content = ""
        for check in skipped_tox_checks:
            warning_content += f"{check} is skipped by packages: {sorted(set(skipped_tox_checks[check]))}. \n"

        if warning_content:
            output_ci_warning(
                    warning_content,
                    "setup_execute_tests.py -> tox_harness.py::prep_and_run_tox",
            )

    return_code = execute_tox_serial(tox_command_tuples)

    if not parsed_args.disablecov:
        collect_tox_coverage_files(targeted_packages)

    sys.exit(return_code)
