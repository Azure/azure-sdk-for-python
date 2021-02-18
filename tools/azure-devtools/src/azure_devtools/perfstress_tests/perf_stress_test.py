# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os


class PerfStressTest:
    '''Base class for implementing a python perf test.  
    
    - run_sync and run_async must be implemented.
    - global_setup and global_cleanup are optional and run once, ever, regardless of parallelism.
    - setup and cleanup are run once per test instance (where each instance runs in its own thread/process), regardless of #iterations.
    - close is run once per test instance, after cleanup and global_cleanup.
    - run_sync/run_async are run once per iteration.
    '''
    args = {}

    def __init__(self, arguments):
        self.args = arguments

    async def global_setup(self):
        return

    async def global_cleanup(self):
        return

    async def setup(self):
        return

    async def cleanup(self):
        return

    async def close(self):
        return

    def __enter__(self):
        return

    def __exit__(self, exc_type, exc_value, traceback):
        return

    def run_sync(self):
        raise Exception('run_sync must be implemented for {}'.format(self.__class__.__name__))

    async def run_async(self):
        raise Exception('run_async must be implemented for {}'.format(self.__class__.__name__))

    @staticmethod
    def add_arguments(parser):
        """
        Override this method to add test-specific argparser args to the class.
        These are accessible in __init__() and the self.args property.
        """
        return

    @staticmethod
    def get_from_env(variable):
        value = os.environ.get(variable)
        if not value:
            raise Exception("Undefined environment variable {}".format(variable))
        return value
