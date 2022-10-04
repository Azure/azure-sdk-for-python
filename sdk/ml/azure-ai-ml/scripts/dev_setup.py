
import logging
import os
import subprocess
import sys
import time

module_logger = logging.getLogger(__name__)


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_red(message):
    print(Color.RED + message + Color.END)


def print_blue(message):
    print(Color.BLUE + message + Color.END)


def run_command(
    commands, cwd=None, stderr=subprocess.STDOUT, shell=False, stream_stdout=True, throw_on_retcode=True, logger=None
):
    if logger is None:
        logger = module_logger

    if cwd is None:
        cwd = os.getcwd()

    t0 = time.perf_counter()
    try:
        logger.debug("Executing {0} in {1}".format(commands, cwd))
        out = ""
        p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=stderr, cwd=cwd, shell=shell)
        for line in p.stdout:
            line = line.decode("utf-8").rstrip()
            if line and line.strip():
                logger.debug(line)
                if stream_stdout:
                    sys.stdout.write(line)
                    sys.stdout.write("\n")
                out += line
                out += "\n"
        p.communicate()
        retcode = p.poll()
        if throw_on_retcode:
            if retcode:
                raise subprocess.CalledProcessError(retcode, p.args, output=out, stderr=p.stderr)
        return retcode, out
    finally:
        t1 = time.perf_counter()
        logger.debug("Execution took {0}s for {1} in {2}".format(t1 - t0, commands, cwd))

if __name__ == "__main__":

    print_blue("Installing dev dependencies...")
    run_command(["pip", "install", "-r", "dev_requirements.txt"])
    run_command(["pip", "install", "tox", "tox-monorepo"])
    run_command(["pip", "install", "-e", "."])
