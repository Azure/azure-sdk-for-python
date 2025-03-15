import os
import sys

from r_proxy_workload import run_workload

sys.path.append(r"./")
from azure.core.pipeline.transport import AioHttpTransport
import asyncio

from datetime import datetime

import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import RotatingFileHandler

# Replace with your Cosmos DB details
os.environ["HTTP_PROXY"] = "http://0.0.0.0:5100"

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
    asyncio.run(run_workload(first_name, logger))
