import sys
import os
import errno
import shutil

if sys.version_info < (3, 0):
    from Queue import Queue
else:
    from queue import Queue
from threading import Thread
import multiprocessing

from subprocess import Popen, PIPE, STDOUT
from common_tasks import process_glob_string, run_check_call, cleanup_folder, clean_coverage, MANAGEMENT_PACKAGE_IDENTIFIERS

import logging
logging.getLogger().setLevel(logging.INFO)

import pdb

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
coverage_dir = os.path.join(root_dir, "_coverage/")
DEFAULT_TOX_INI_LOCATION = os.path.join(root_dir, "eng/tox/tox.ini")

class ToxWorkItem:
    def __init__(self, target_package_path, tox_env, options_array):
        self.target_package_path = target_package_path
        self.tox_env = tox_env
        self.options_array = options_array

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
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
                print(e)
            finally:
                self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

# TODO, dedup this function with collect_pytest
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

def execute_tox_parallel(tox_command_tuples):
    procs_list = []

    for index, cmd_tuple in enumerate(tox_command_tuples):
        package_dir = cmd_tuple[1]

        logging.info(
            "Starting tox for {}. {} of {}.".format(
                os.path.basename(package_dir), index, len(tox_command_tuples)
            )
        )

        with open(os.path.join(package_dir, 'stdout.txt'), 'w') as f_stdout, open(os.path.join(package_dir, 'stderr.txt'), 'w') as f_stderr:
            proc = Popen(cmd_tuple[0], stdout=f_stdout, stderr=f_stderr, cwd=package_dir, env=os.environ.copy())
            procs_list.append(proc)

    failed_test_run = False

    for index, proc in enumerate(procs_list):
        proc.wait()

        if proc.returncode != 0:
            logging.error("Package returned with code {}".format(proc.returncode))

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
        if not os.path.exists(destination_tox_ini):
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

        tox_command_tuples.append((tox_execution_array, package_dir))

    if is_parallel:
        execute_tox_parallel(tox_command_tuples)
    else:
        for index, cmd_tuple in enumerate(tox_command_tuples):
            logging.info(
                "Running tox for {}. {} of {}.".format(
                    os.path.basename(cmd_tuple[1]), index, len(tox_command_tuples)
                )
            )
            run_check_call(cmd_tuple[0], cmd_tuple[1])

    # TODO: get a bit smarter here
    if not tox_env:
        collect_tox_coverage_files(targeted_packages)


# def execute_parallel_workload(workload_callback, targeted_packages, tox_env, options_array):
#     work_items = []
#     pool_size = multiprocessing.cpu_count() * 2
#     for pkg in targeted_packages:
#         work_items.append(ToxWorkItem(pkg, tox_env, options_array))

#     pool = ThreadPool(1)

#     for i, d in enumerate(work_items):
#         pool.add_task(workload_callback, d)
#     pool.wait_completion()


# Reference implementation
# if __name__ == '__main__':
#     from time import sleep

#     delays = [randrange(1, 10) for i in range(100)]

#     def wait_delay(d):
#         print('sleeping for (%d)sec' % d)
#         sleep(d)

#     pool = ThreadPool(20)

#     for i, d in enumerate(delays):
#         pool.add_task(wait_delay, d)

#     pool.wait_completion()