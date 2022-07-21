# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging
from typing import Union, Optional, Any
from time import time
from concurrent.futures import Future

from azure.mgmt.core.polling.arm_polling import ARMPolling
from azure.ai.ml.constants import LROConfigurations
from azure.core.polling import LROPoller


module_logger = logging.getLogger(__name__)


class AzureMLPolling(ARMPolling):
    """
    A polling class for azure machine learning
    """

    def update_status(self):
        """Update the current status of the LRO."""
        super(ARMPolling, self).update_status()


def polling_wait(
    poller: Union[LROPoller, Future], message: Optional[str] = None, start_time: Optional[float] = None
) -> Any:
    """Print out status while polling and time of operation once completed.

    :param poller: An poller which will return status update via function done().
    :type poller: Union[LROPoller, concurrent.futures.Future]
    :param message: Message to print out before starting operation write-out.
    :type message: Optional[str]
    :param start_time: Start time of operation.
    :type start_time: Optional[float]
    """
    module_logger.info(f"{message}")
    poller.result(timeout=LROConfigurations.POLLING_TIMEOUT)
    module_logger.info("Done.")

    if start_time:
        end_time = time()
        duration = divmod(int(round(end_time - start_time)), 60)
        module_logger.info(f"({duration[0]}m {duration[1]}s)\n")
