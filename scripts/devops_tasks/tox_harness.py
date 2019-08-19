import sys
if sys.version_info < (3, 0):
    from Queue import Queue
else:
    from queue import Queue
from threading import Thread
import multiprocessing
import pdb

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

def prep_and_run_tox(targeted_packages, tox_env, options_array=[]):

    for index, package_dir in enumerate(targeted_packages):
        logging.info(
            "Running tox for {}. {} of {}.".format(
                package_dir, index, len(targeted_packages)
            )
        )
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

        run_check_call(tox_execution_array, package_dir)

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