from subprocess import check_call
import logging
import sys
import os

logging.getLogger().setLevel(logging.INFO)
root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

def import_all(namespace):
    logging.info(
        "Importing all modules from namespace [{0}] to verify dependency".format(
            namespace
        )
    )
    import_script_all = "from {0} import *".format(namespace)
    commands = [
        sys.executable,
        "-c",
        import_script_all
    ]

    check_call(commands, cwd= root_dir)
    logging.info("Verified module dependency, no issues found")

if __name__ == '__main__':
    parser.