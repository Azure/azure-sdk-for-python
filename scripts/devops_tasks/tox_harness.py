import sys
import os
import errno
import shutil
import re
import multiprocessing
import glob
import pdb

if sys.version_info < (3, 0):
    from Queue import Queue
else:
    from queue import Queue
from threading import Thread

from subprocess import Popen, PIPE, STDOUT
from common_tasks import (
    run_check_call,
    clean_coverage,
    log_file,
    read_file,
    is_error_code_5_allowed,
    create_code_coverage_params,
    find_whl
)

from ci_tools.functions import discover_targeted_packages
from ci_tools.parsing import ParsedSetup

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

class ToxWorkItem:
    def __init__(self, target_package_path, tox_env, options_array):
        self.target_package_path = target_package_path
        self.tox_env = tox_env
        self.options_array = options_array


class Worker(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                logging.error(e)
            finally:
                self.tasks.task_done()


def in_ci():
    return os.getenv("TF_BUILD", False)


class ThreadPool:
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        self.tasks.join()


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
            destination_file = os.path.join(
                root_coverage_dir, ".coverage_{}".format(os.path.basename(package_dir))
            )
            shutil.copyfile(coverage_file, destination_file)
            coverage_files.append(destination_file)

    logging.info("Uploading .coverage files: {}".format(coverage_files))



def individual_workload(tox_command_tuple, workload_results):
    pkg = os.path.basename(tox_command_tuple[1])
    stdout = os.path.join(tox_command_tuple[1], "stdout.txt")
    stderr = os.path.join(tox_command_tuple[1], "stderr.txt")
    tox_dir = os.path.join(tox_command_tuple[1], "./.tox/")

    with open(stdout, "w") as f_stdout, open(stderr, "w") as f_stderr:
        proc = Popen(
            tox_command_tuple[0],
            stdout=f_stdout,
            stderr=f_stderr,
            cwd=tox_command_tuple[1],
            env=os.environ.copy(),
        )

        logging.info("POpened task for for {}".format(pkg))
        proc.wait()

        return_code = proc.returncode

        if proc.returncode != 0:
            logging.error("{} returned with code {}".format(pkg, proc.returncode))
        else:
            logging.info(
                "{} returned with code 0, output will be printed after the test run completes.".format(
                    pkg
                )
            )

        if read_file(stderr):
            logging.error("Package {} had stderror output. Logging.".format(pkg))
            return_code = "StdErr output detected"

        workload_results[tox_command_tuple[1]] = (return_code, stdout, stderr)

        if in_ci():
            shutil.rmtree(tox_dir)


def execute_tox_parallel(tox_command_tuples):
    pool = ThreadPool(pool_size)
    workload_results = {}
    run_result = 0

    for index, cmd_tuple in enumerate(tox_command_tuples):
        pool.add_task(individual_workload, cmd_tuple, workload_results)

    pool.wait_completion()

    for key in workload_results.keys():
        log_file(workload_results[key][1])

        if workload_results[key][0] != 0:
            logging.error(
                "{} tox invocation exited with returncode {}".format(
                    os.path.basename(key), workload_results[key][0]
                )
            )
            run_result = 1

    return run_result


def compare_req_to_injected_reqs(parsed_req, injected_packages):
    if parsed_req is None:
        return False

    return any(parsed_req.name in req for req in injected_packages)


def inject_custom_reqs(file, injected_packages, package_dir):
    req_lines = []
    injected_packages = [p for p in re.split("[\s,]", injected_packages) if p]

    if injected_packages:
        logging.info(
            "Adding custom packages to requirements for {}".format(package_dir)
        )
        with open(file, "r") as f:
            for line in f:
                try:
                    parsed_req = [req for req in parse_requirements(line)]
                except RequirementParseError as e:
                    parsed_req = [None]
                req_lines.append((line, parsed_req))

        if req_lines:
            all_adjustments = injected_packages + [
                line_tuple[0].strip()
                for line_tuple in req_lines
                if line_tuple[0].strip()
                and not compare_req_to_injected_reqs(
                    line_tuple[1][0], injected_packages
                )
            ]
        else:
            all_adjustments = injected_packages

        with open(file, "w") as f:
            # note that we directly use '\n' here instead of os.linesep due to how f.write() actually handles this stuff internally
            # If a file is opened in text mode (the default), during write python will accidentally double replace due to "\r" being
            # replaced with "\r\n" on Windows. Result: "\r\n\n". Extra line breaks!
            f.write("\n".join(all_adjustments))


def build_whl_for_req(req, package_path):
    if ".." in req:
        # Create temp path if it doesn't exist
        temp_dir = os.path.join(package_path, ".tmp_whl_dir")
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

        req_pkg_path = os.path.abspath(os.path.join(package_path, req.replace("\n", "")))
        parsed = ParsedSetup.from_path(req_pkg_path)

        logging.info("Building wheel for package {}".format(parsed.name))
        run_check_call([sys.executable, "setup.py", "bdist_wheel", "-d", temp_dir], req_pkg_path)

        whl_path = os.path.join(temp_dir, find_whl(parsed.name, parsed.version, temp_dir))
        logging.info("Wheel for package {0} is {1}".format(parsed.name, whl_path))
        logging.info("Replacing dev requirement. Old requirement:{0}, New requirement:{1}".format(req, whl_path))
        return whl_path
    else:
        return req

def replace_dev_reqs(file, pkg_root):
    adjusted_req_lines = []

    with open(file, "r") as f:
        for line in f:
            args = [
                part.strip()
                for part in line.split()
                if part and not part.strip() == "-e"
            ]
            amended_line = " ".join(args)
            adjusted_req_lines.append(amended_line)

    req_file_name = os.path.basename(file)
    logging.info("Old {0}:{1}".format(req_file_name, adjusted_req_lines))

    adjusted_req_lines = list(map(lambda x: build_whl_for_req(x, pkg_root), adjusted_req_lines))
    logging.info("New {0}:{1}".format(req_file_name, adjusted_req_lines))

    with open(file, "w") as f:
        # note that we directly use '\n' here instead of os.linesep due to how f.write() actually handles this stuff internally
        # If a file is opened in text mode (the default), during write python will accidentally double replace due to "\r" being
        # replaced with "\r\n" on Windows. Result: "\r\n\n". Extra line breaks!
        f.write("\n".join(adjusted_req_lines))


def collect_log_files(working_dir):
    logging.info("Collecting log files from {}".format(working_dir))
    package = working_dir.split('/')[-1]
    # collect all the log files into one place for publishing in case of tox failure

    log_directory = os.path.join(
        root_dir, "_tox_logs"
    )

    try:
        os.mkdir(log_directory)
        logging.info("Created log directory: {}".format(log_directory))
    except OSError:
        logging.info("'{}' directory already exists".format(log_directory))

    log_directory = os.path.join(
        log_directory, package
    )

    try:
        os.mkdir(log_directory)
        logging.info("Created log directory: {}".format(log_directory))
    except OSError:
        logging.info("'{}' directory already exists".format(log_directory))

    log_directory = os.path.join(
        log_directory, sys.version.split()[0]
    )

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
                    shutil.move(
                        file_location,
                        os.path.join(temp_dir, filename)
                    )
                    logging.info("Moved file to {}".format(os.path.join(temp_dir, filename)))
        else:
            logging.info("Could not find {} directory".format(log_files))

    for f in glob.glob(os.path.join(root_dir, "_tox_logs", "*")):
        logging.info("Log file: {}".format(f))


def execute_tox_serial(tox_command_tuples):
    return_code = 0

    for index, cmd_tuple in enumerate(tox_command_tuples):
        tox_dir = os.path.abspath(os.path.join(cmd_tuple[1], "./.tox/"))
        logging.info("tox_dir: {}".format(tox_dir))

        logging.info(
            "Running tox for {}. {} of {}.".format(
                os.path.basename(cmd_tuple[1]), index + 1, len(tox_command_tuples)
            )
        )

        result = run_check_call(cmd_tuple[0], cmd_tuple[1], always_exit=False)

        if result is not None and result != 0:
            return_code = result

        if in_ci():
            collect_log_files(cmd_tuple[1])
            shutil.rmtree(tox_dir)

    return return_code


def prep_and_run_tox(targeted_packages, parsed_args, options_array=[]):
    if parsed_args.wheel_dir:
        os.environ["PREBUILT_WHEEL_DIR"] = parsed_args.wheel_dir

    if parsed_args.mark_arg:
        options_array.extend(["-m", "{}".format(parsed_args.mark_arg)])

    tox_command_tuples = []

    for index, package_dir in enumerate(targeted_packages):
        destination_tox_ini = os.path.join(package_dir, "tox.ini")
        destination_dev_req = os.path.join(package_dir, "dev_requirements.txt")

        tox_execution_array = [sys.executable, "-m", "tox"]

        local_options_array = options_array[:]

        # Get code coverage params for current package
        package_name = os.path.basename(package_dir)
        coverage_commands = create_code_coverage_params(parsed_args, package_name)
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
            os.path.exists(destination_tox_ini)
            and os.path.basename(package_dir) in IGNORED_TOX_INIS
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

        inject_custom_reqs(
            destination_dev_req, parsed_args.injected_packages, package_dir
        )

        if parsed_args.tox_env:
            tox_execution_array.extend(["-e", parsed_args.tox_env])

        if parsed_args.tenvparallel:
            tox_execution_array.extend(["-p", "all"])

        if parsed_args.tox_env == "apistub":
            local_options_array = []
            if parsed_args.dest_dir:
                local_options_array.extend(["--out-path", parsed_args.dest_dir])

        if local_options_array:
            tox_execution_array.extend(["--"] + local_options_array)

        tox_command_tuples.append((tox_execution_array, package_dir))

    if parsed_args.tparallel:
        return_code = execute_tox_parallel(tox_command_tuples)
    else:
        return_code = execute_tox_serial(tox_command_tuples)

    if not parsed_args.disablecov:
        collect_tox_coverage_files(targeted_packages)

    sys.exit(return_code)