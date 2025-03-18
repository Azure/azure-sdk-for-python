import os
import sys

from r_w_q_workload_sync import run_workload

sys.path.append(r"./")


from datetime import datetime

import logging
from logging.handlers import RotatingFileHandler

if __name__ == "__main__":
    logger = logging.getLogger('azure.cosmos')
    file_name = os.path.basename(__file__)
    first_name = file_name.split(".")[0]
    # Create a rotating file handler
    handler = RotatingFileHandler(
        "log-" + first_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log',
        maxBytes=1024 * 1024 * 10, # 10 mb
        backupCount=3
    )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    run_workload(first_name, logger)
