# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import psutil
import threading
import time

from logger import get_base_logger


class ProcessMonitor:
    def __init__(self, log_filename, logger_name, log_interval=5.0, print_console=False,
                 process_id=None, **kwargs):
        """
        Process Monitor monitors the CPU usage, memory usage of a specific process.

        :param logger_filename: The log filename for the logger.
        :param logger_name: The name for the logger.
        :param log_interval: The interval of logging.
        :param print_console: Whether output log content to console. Default is False.
        :param process_id: The process id of the process if monitor, if this is set None, then it will monitor
         the process that the ProcessMonitor is running in.
        """
        self._monitor_thread = None
        self._logger = get_base_logger(
            log_filename=log_filename,
            logger_name=logger_name,
            print_console=print_console,
            **kwargs
        )
        self._pid = process_id or os.getpid()
        self._process_instance = psutil.Process(self._pid)
        self._log_interval = log_interval
        self.running = False

    def __enter__(self):
        print('Process monitor start working.')
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
        print('Process monitor stop working.')

    def _monitor_work(self):
        while self.running:
            log_content = "process status: {}," \
                "process cpu usage percent: {}," \
                "process memory usage percent: {:.3f}".format(
                    self._process_instance.status(),
                    self._process_instance.cpu_percent(),
                    self._process_instance.memory_percent()
                )
            self._logger.info(log_content)
            time.sleep(self._log_interval)

    @property
    def memory_usage_percent(self):
        return self._process_instance.memory_percent() * 100

    @property
    def cpu_usage_percent(self):
        return self._process_instance.cpu_percent()

    def start(self):
        self.running = True
        self._monitor_thread = threading.Thread(target=self._monitor_work, daemon=True)
        self._monitor_thread.start()
        self._logger.info("Start monitoring process id:{}".format(self._pid))

    def stop(self):
        self.running = False
        self._monitor_thread.join()
        self._logger.info("Stop monitoring process id:{}".format(self._pid))
        self._monitor_thread = None
