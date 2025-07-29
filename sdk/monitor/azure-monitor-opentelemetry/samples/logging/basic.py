# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from logging import INFO, Formatter, getLogger

from azure.monitor.opentelemetry import configure_azure_monitor

# logging.basicConfig and logging.config will be overwritten by the SDK
# We recommend using logger specific configuration or the below apis to configure logging

configure_azure_monitor(
    # Set logger_name to the name of the logger you want to capture logging telemetry with
    # This is imperative so you do not collect logging telemetry from the SDK itself.
    logger_name="my_app_logger",
    # You can specify the logging format of your collected logs by passing in a logging.Formatter
    logging_formatter=Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# Logging telemetry will be collected from logging calls made with this logger and all of it's children loggers.
logger = getLogger("my_app_logger")
logger.setLevel(INFO)

# Logging calls with any logger that is a child logger will also be tracked
logger_child = getLogger("my_app_logger.module")
logger_child.setLevel(INFO)

# Logging calls with this logger will not be tracked
logger_not_tracked = getLogger("not_my_app_logger")
logger_not_tracked.setLevel(INFO)

logger.info("info log")
logger.warning("warning log")
logger.error("error log")

logger_child.info("Child: info log")
logger_child.warning("Child: warning log")
logger_child.error("Child: error log")

logger_not_tracked.info("Not tracked: info log")
logger_not_tracked.warning("Not tracked: warning log")
logger_not_tracked.error("Not tracked: error log")

input()
