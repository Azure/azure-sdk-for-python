# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from logging import INFO, getLogger

import flask
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

logger = getLogger(__name__)
logger.setLevel(INFO)

app = flask.Flask(__name__)


@app.route("/info_log")
def info_log():
    message = "Correlated info log"
    logger.info(message)
    return message


@app.route("/error_log")
def error_log():
    message = "Correlated error log"
    logger.error(message)
    return message


if __name__ == "__main__":
    app.run(host="localhost", port=8080)
