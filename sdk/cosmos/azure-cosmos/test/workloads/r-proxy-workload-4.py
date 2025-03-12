import os
import sys

from r_proxy_workload import run_workload

sys.path.append(r"./")
from azure.core.pipeline.transport import AioHttpTransport
import asyncio

from datetime import datetime

import logging

# Replace with your Cosmos DB details
os.environ["HTTP_PROXY"] = "http://0.0.0.0:5100"

if __name__ == "__main__":
    logger = logging.getLogger('azure.cosmos')
    file_name = os.path.basename(__file__)
    first_name = file_name.split(".")[0]
    file_handler = logging.FileHandler("log-" + first_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    asyncio.run(run_workload(first_name, logger))
