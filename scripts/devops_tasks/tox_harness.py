import sys
import os
import errno
import shutil
import multiprocessing

if sys.version_info < (3, 0):
    from Queue import Queue
else:
    from queue import Queue
from threading import Thread

from subprocess import Popen, PIPE, STDOUT
from common_tasks import (
    process_glob_string,
    run_check_call,
    cleanup_folder,
    clean_coverage,
    log_file,
    read_file,
    is_error_code_5_allowed,
    create_code_coverage_params,
)

import logging

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
coverage_dir = os.path.join(root_dir, "_coverage/")
pool_size = multiprocessing.cpu_count() * 2
DEFAULT_TOX_INI_LOCATION = os.path.join(root_dir, "eng/tox/tox.ini")
IGNORED_TOX_INIS = ["azure-cosmos"]


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

    # coverage report has paths starting .tox and azure
    # coverage combine fixes this with the help of tox.ini[coverage:paths]
    combine_coverage_files(targeted_packages)

    coverage_files = []
    # generate coverage files
    for package_dir in [package for package in targeted_packages]:
        coverage_file = os.path.join(package_dir, ".coverage")
        if os.path.isfile(coverage_file):
            destination_file = os.path.join(
                root_coverage_dir, ".coverage_{}".format(os.path.basename(package_dir))
            )
            shutil.copyfile(coverage_file, destination_file)
            coverage_files.append(destination_file)

    logging.info("Visible uncombined .coverage files: {}".format(coverage_files))

    if len(coverage_files):
        cov_cmd_array = [sys.executable, "-m", "coverage", "combine"]
        cov_cmd_array.extend(coverage_files)

        # merge them with coverage combine and copy to root
        run_check_call(cov_cmd_array, os.path.join(root_dir, "_coverage/"))

        source = os.path.join(coverage_dir, "./.coverage")
        dest = os.path.join(root_dir, ".coverage")

        shutil.move(source, dest)


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
    failed_run = False

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
            failed_run = True

    if failed_run:
        exit(1)


def replace_dev_reqs(file):
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

    with open(file, "w") as f:
        # note that we directly use '\n' here instead of os.linesep due to how f.write() actually handles this stuff internally
        # If a file is opened in text mode (the default), during write python will accidentally double replace due to "\r" being
        # replaced with "\r\n" on Windows. Result: "\r\n\n". Extra line breaks!
        f.write("\n".join(adjusted_req_lines))


def execute_tox_serial(tox_command_tuples):
    for index, cmd_tuple in enumerate(tox_command_tuples):
        tox_dir = os.path.join(cmd_tuple[1], "./.tox/")

        logging.info(
            "Running tox for {}. {} of {}.".format(
                os.path.basename(cmd_tuple[1]), index + 1, len(tox_command_tuples)
            )
        )
        run_check_call(cmd_tuple[0], cmd_tuple[1])

        if in_ci():
            shutil.rmtree(tox_dir)


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
            replace_dev_reqs(destination_dev_req)
            os.environ["TOX_PARALLEL_NO_SPINNER"] = "1"

        if parsed_args.tox_env:
            tox_execution_array.extend(["-e", parsed_args.tox_env])

       # if parsed_args.tenvparallel:
            #tox_execution_array.extend(["-p", "all"])

        if local_options_array:
            tox_execution_array.extend(["--"] + local_options_array)

        tox_command_tuples.append((tox_execution_array, package_dir))

    if parsed_args.tparallel:
        execute_tox_parallel(tox_command_tuples)
    else:
        execute_tox_serial(tox_command_tuples)

    if not parsed_args.disablecov:
        collect_tox_coverage_files(targeted_packages)
