# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from utils import print_blue, run_command

module_logger = logging.getLogger(__name__)

if __name__ == "__main__":

    print_blue("Installing dev dependencies...")
    run_command(["pip", "install", "-r", "dev_requirements.txt"])
    run_command(["pip", "install", "tox", "tox-monorepo"])
    run_command(["pip", "install", "-e", "."])
