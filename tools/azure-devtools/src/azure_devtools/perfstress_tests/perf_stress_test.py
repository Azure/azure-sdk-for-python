import random
import string

class PerfStressTest:
    '''Base class for implementing a python perf test.  
    
- Run and RunAsync must be implemented.
- GlobalSetup and GlobalCleanup are optional and run once, ever, regardless of parallelism.
- Setup and Cleanup are run once per test instance (where each instance runs in its own thread/process), regardless of #iterations.
- Close is run once per test instance, after Cleanup and GlobalCleanup.
- Run/RunAsync are run once per iteration.'''
    def __init__(self, arguments):
        self.Arguments = arguments

    async def GlobalSetupAsync(self):
        return

    async def GlobalCleanupAsync(self):
        return

    async def SetupAsync(self):
        return

    async def CleanupAsync(self):
        return

    async def CloseAsync(self):
        return

    def __enter__(self):
        return

    def __exit__(self, exc_type, exc_value, traceback):
        return

    def Run(self):
        raise Exception('Run must be implemented for {}'.format(self.__class__.__name__))

    async def RunAsync(self):
        raise Exception('RunAsync must be implemented for {}'.format(self.__class__.__name__))

    Arguments = {}
    # Override this method to add test-specific argparser args to the class.
    # These are accessible in __init__() and the self.Arguments property.
    @staticmethod
    def AddArguments(parser):
        return
