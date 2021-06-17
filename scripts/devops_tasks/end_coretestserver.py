import os
import signal
import argparse

def end_testserver(pid):

    if os.name == 'nt':
        os.kill(pid, signal.CTRL_C_EVENT)
    else:
        os.killpg(os.getpgid(pid), signal.SIGTERM)  # Send the signal to all the process groups

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Stop the testserver"
    )
    parser.add_argument(
        "-p",
        "--pid",
        dest="pid",
        help="The pid of the subprocess the testserver is running on",
        required=True,
    )

    args = parser.parse_args()
    end_testserver(int(args.pid))
