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
    MANAGEMENT_PACKAGE_IDENTIFIERS,
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


def collect_tox_coverage_files(targeted_packages):
    root_coverage_dir = os.path.join(root_dir, "_coverage/")

    clean_coverage(coverage_dir)

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
        cov_cmd_array = ["coverage", "combine"]
        cov_cmd_array.extend(coverage_files)

        # merge them with coverage combine and copy to root
        run_check_call(cov_cmd_array, os.path.join(root_dir, "_coverage/"))

        source = os.path.join(coverage_dir, "./.coverage")
        dest = os.path.join(root_dir, ".coverage")

        shutil.move(source, dest)


def individual_workload(tox_command_tuple, failed_workload_results):
    stdout = os.path.join(tox_command_tuple[1], "stdout.txt")
    stderr = os.path.join(tox_command_tuple[1], "stderr.txt")
    pkg = os.path.basename(tox_command_tuple[1])

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

        log_file(stdout)

        if proc.returncode != 0:
            logging.error("{} returned with code {}".format(pkg, proc.returncode))
            failed_workload_results[pkg] = proc.returncode

        if read_file(stderr):
            logging.error("Package {} had stderror output. Logging.".format(pkg))
            failed_workload_results[pkg] = "StdErr output detected"
            log_file(stderr)

    return proc


def execute_tox_parallel(tox_command_tuples):
    pool = ThreadPool(pool_size)
    failed_workload_results = {}

    for index, cmd_tuple in enumerate(tox_command_tuples):
        pool.add_task(individual_workload, cmd_tuple, failed_workload_results)

    pool.wait_completion()

    if len(failed_workload_results.keys()):
        for key in failed_workload_results.keys():
            logging.error(
                "{} tox invocation exited with returncode {}".format(
                    key, failed_workload_results[key]
                )
            )
        exit(1)


def execute_tox_serial(tox_command_tuples):
    for index, cmd_tuple in enumerate(tox_command_tuples):
        logging.info(
            "Running tox for {}. {} of {}.".format(
                os.path.basename(cmd_tuple[1]), index + 1, len(tox_command_tuples)
            )
        )
        run_check_call(cmd_tuple[0], cmd_tuple[1])


def prep_and_run_tox(targeted_packages, tox_env, options_array=[], is_parallel=False):
    tox_command_tuples = []

    for index, package_dir in enumerate(targeted_packages):
        destination_tox_ini = os.path.join(package_dir, "tox.ini")
        destination_dev_req = os.path.join(package_dir, "dev_requirements.txt")
        tox_execution_array = ["tox"]
        local_options_array = options_array[:]

        # if we are targeting only packages that are management plane, it is a possibility
        # that no tests running is an acceptable situation
        # we explicitly handle this here.
        if all(
            map(
                lambda x: any(
                    [pkg_id in x for pkg_id in MANAGEMENT_PACKAGE_IDENTIFIERS]
                ),
                [package_dir],
            )
        ):
            local_options_array.append("--suppress-no-test-exit-code")

        # if not present, re-use base
        if not os.path.exists(destination_tox_ini) or (
            os.path.exists(destination_tox_ini)
            and os.path.basename(package_dir) in IGNORED_TOX_INIS
        ):
            logging.info("No customized tox.ini present, using common eng/tox/tox.ini.")
            tox_execution_array.extend(["-c", DEFAULT_TOX_INI_LOCATION])

        # handle empty file
        if not os.path.exists(destination_dev_req):
            logging.info("No dev_requirements present.")
            with open(destination_dev_req, "w+") as file:
                file.write("-e ../../../tools/azure-sdk-tools")

        if tox_env:
            tox_execution_array.extend(["-e", tox_env])

        if local_options_array:
            tox_execution_array.extend(["--"] + local_options_array)

        # 0 = command array
        tox_command_tuples.append((tox_execution_array, package_dir))

    if is_parallel:
        execute_tox_parallel(tox_command_tuples)
    else:
        execute_tox_serial(tox_command_tuples)

    # TODO: get a bit smarter here
    if not tox_env:
        collect_tox_coverage_files(targeted_packages)
