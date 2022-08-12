import signal

_PIPELINE_JOB_TIMEOUT_SECOND = 20 * 60  # timeout for pipeline job's tests, unit in second.
_PYTEST_TIMEOUT_METHOD = "signal" if hasattr(signal, "SIGALRM") else "thread"  # use signal when os support SIGALRM
