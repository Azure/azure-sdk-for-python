# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

"""Contains functionality for sending telemetry to Application Insights."""

import datetime
import json
import logging
import platform
import urllib.request as http_client_t
from os import getenv
from urllib.error import HTTPError

from applicationinsights import TelemetryClient
from applicationinsights.channel import (
    AsynchronousQueue,
    AsynchronousSender,
    SynchronousQueue,
    SynchronousSender,
    TelemetryChannel,
    TelemetryContext,
)

from .._user_agent import USER_AGENT
from ._customtraceback import format_exc

AML_INTERNAL_LOGGER_NAMESPACE = "azure.ai.ml._telemetry"

# vienna-sdk-unitedstates
INSTRUMENTATION_KEY = "71b954a8-6b7d-43f5-986c-3d3a6605d803"

AZUREML_SDKV2_TELEMETRY_OPTOUT_ENV_VAR = "AZUREML_SDKV2_TELEMETRY_OPTOUT"

# application insight logger name
LOGGER_NAME = "ApplicationInsightLogger"

SUCCESS = True
FAILURE = False

TRACEBACK_LOOKUP_STR = "Traceback (most recent call last)"

# extract traceback path from message
reformat_traceback = True

test_subscriptions = [
    "b17253fa-f327-42d6-9686-f3e553e24763",
    "test_subscription",
    "6560575d-fa06-4e7d-95fb-f962e74efd7a",
    "b17253fa-f327-42d6-9686-f3e553e2452",
    "74eccef0-4b8d-4f83-b5f9-fa100d155b22",
    "4faaaf21-663f-4391-96fd-47197c630979",
]


def is_telemetry_collection_disabled():
    telemetry_disabled = getenv(AZUREML_SDKV2_TELEMETRY_OPTOUT_ENV_VAR)
    return telemetry_disabled and (telemetry_disabled.lower() == "true" or telemetry_disabled == "1")


def get_appinsights_log_handler(user_agent, instrumentation_key=None, component_name=None, *args, **kwargs):
    """Enable the Application Insights logging handler for specified logger and
    instrumentation key.

    Enable diagnostics collection with the :func:`azureml.telemetry.set_diagnostics_collection` function.

    :param instrumentation_key: The Application Insights instrumentation key.
    :type instrumentation_key: str
    :param component_name: The component name.
    :type component_name: str
    :param args: Optional arguments for formatting messages.
    :type args: list
    :param kwargs: Optional keyword arguments for adding additional information to messages.
    :type kwargs: dict
    :return: The logging handler.
    :rtype: logging.Handler
    """
    try:
        if instrumentation_key is None:
            instrumentation_key = INSTRUMENTATION_KEY

        if is_telemetry_collection_disabled():
            return logging.NullHandler()

        if not user_agent or not user_agent.lower() == USER_AGENT.lower():
            return logging.NullHandler()

        if "properties" in kwargs and "subscription_id" in kwargs.get("properties"):
            if kwargs.get("properties")["subscription_id"] in test_subscriptions:
                return logging.NullHandler()

        child_namespace = component_name or __name__
        current_logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE).getChild(child_namespace)
        current_logger.propagate = False
        current_logger.setLevel(logging.CRITICAL)

        context = TelemetryContext()
        custom_properties = {"PythonVersion": platform.python_version()}
        custom_properties.update({"user_agent": user_agent})
        if "properties" in kwargs:
            context._properties.update(kwargs.pop("properties"))
        context._properties.update(custom_properties)
        handler = AppInsightsLoggingHandler(instrumentation_key, current_logger, telemetry_context=context)

        return handler
    except Exception:
        # ignore exceptions, telemetry should not block
        return logging.NullHandler()


class AppInsightsLoggingHandler(logging.Handler):
    """Integration point between Python's logging framework and the Application
    Insights service.

    :param instrumentation_key: The instrumentation key to use while sending telemetry to the Application
        Insights service.
    :type instrumentation_key: str
    :param logger:
    :type logger: logger
    :param sender: The Application Insight sender object.
    :type sender: SynchronousSender
    :param args: Optional arguments for formatting messages.
    :type args: list
    :param kwargs: Optional keyword arguments for adding additional information to messages.
    :type kwargs: dict
    """

    def __init__(self, instrumentation_key, logger, sender=None, *args, **kwargs):
        """Initialize a new instance of the class.

        :param instrumentation_key: The instrumentation key to use while sending telemetry to the Application
            Insights service.
        :type instrumentation_key: str
        :param sender: The Application Insight sender object.
        :type sender: SynchronousSender
        :param args: Optional arguments for formatting messages.
        :type args: list
        :param kwargs: Optional keyword arguments for adding additional information to messages.
        :type kwargs: dict
        """
        if not instrumentation_key:
            raise Exception("Instrumentation key was required but not provided")

        telemetry_context = None
        if "telemetry_context" in kwargs:
            telemetry_context = kwargs.pop("telemetry_context")
        else:
            telemetry_context = TelemetryContext()

        if "properties" in kwargs:
            telemetry_context._properties.update(kwargs.pop("properties"))

        self.logger = logger
        self._sender = sender or _RetrySynchronousSender

        # Configuring an asynchronous client as default telemetry client (fire and forget mode)
        self._default_client = TelemetryClient(
            instrumentation_key, self._create_asynchronous_channel(telemetry_context)
        )

        #  Configuring a synchronous client and should be only used in critical scenarios
        self._synchronous_client = TelemetryClient(
            instrumentation_key, self._create_synchronous_channel(telemetry_context)
        )

        super(AppInsightsLoggingHandler, self).__init__(*args, **kwargs)

    def flush(self):
        """Flush the queued up telemetry to the service."""
        self._default_client.flush()
        return super(AppInsightsLoggingHandler, self).flush()

    def emit(self, record):
        """Emit a log record.

        :param record: The log record to format and send.
        :type record: logging.LogRecord
        """
        if is_telemetry_collection_disabled():
            return
        try:
            if (
                reformat_traceback
                and record.levelno >= logging.WARNING
                and hasattr(record, "message")
                and record.message.find(TRACEBACK_LOOKUP_STR) != -1
            ):
                record.message = format_exc()
                record.msg = record.message

            properties = {"level": record.levelname}
            properties.update(self._default_client.context.properties)

            formatted_message = self.format(record)

            if hasattr(record, "properties"):
                properties.update(record.properties)
            # if we have exec_info, send it as an exception
            if record.exc_info and not all(item is None for item in record.exc_info):
                # for compliance we not allowed to collect trace with file path
                self._synchronous_client.track_trace(format_exc(), severity=record.levelname, properties=properties)
                return
            # otherwise, send the trace
            self._default_client.track_trace(formatted_message, severity=record.levelname, properties=properties)
        except Exception:
            # ignore exceptions, telemetry should not block because of trimming
            return

    def _create_synchronous_channel(self, context):
        """Create a synchronous app insight channel.

        :param context: The Application Insights context.
        :return: TelemetryChannel
        """
        channel = TelemetryChannel(context=context, queue=SynchronousQueue(self._sender(self.logger)))
        # the behavior is same to call flush every time
        channel.queue.max_queue_length = 1
        return channel

    def _create_asynchronous_channel(self, context):
        """Create an async app insight channel.

        :param context: The Applications Insights context.
        :return: TelemetryChannel
        """
        sender = _RetryAsynchronousSender(self.logger)
        queue = AsynchronousQueue(sender)
        channel = TelemetryChannel(context, queue)

        # flush telemetry if we have 10 or more telemetry items in our queue
        channel.queue.max_queue_length = 10
        # send telemetry to the service in batches of 10
        channel.sender.send_buffer_size = 10
        # the background worker thread will be active for 1 seconds before it shuts down. if
        # during this time items are picked up from the queue, the timer is reset.
        channel.sender.send_time = 1
        # the background worker thread will poll the queue every 0.1 seconds for new items
        # 100ms is the most aggressive setting we can set
        channel.sender.send_interval = 0.1

        return channel


class _RetrySynchronousSender(SynchronousSender):
    """Synchronous sender with limited retry.

    SenderBase does infinite retry; this class avoids that.
    """

    def __init__(self, logger, timeout=10, retry=1):
        super(_RetrySynchronousSender, self).__init__()
        self._logger = logger
        self.send_timeout = timeout
        self.retry = retry
        self.consecutive_failures = 0

    def send(self, data_to_send):
        """Override the default resend mechanism in SenderBase.

        Stop resend based on retry during failure.
        """
        status = _http_send(self._logger, data_to_send, self.service_endpoint_uri, self.send_timeout)
        if status is SUCCESS:
            self.consecutive_failures = 0
            return
        else:
            self.consecutive_failures = self.consecutive_failures + 1

        if self.consecutive_failures <= self.retry:
            for data in data_to_send:
                self._queue.put(data)


class _RetryAsynchronousSender(AsynchronousSender):
    """Asynchronous sender with limited retry.

    SenderBase does infinite retry; this class avoids that.
    """

    def __init__(self, logger, timeout=10, retry=3):
        super(_RetryAsynchronousSender, self).__init__()
        self._logger = logger
        self.send_timeout = timeout
        self.retry = retry
        self.consecutive_failures = 0

    def send(self, data_to_send):
        """Override the default resend mechanism in SenderBase.

        Stop resend based on retry during failure.
        """
        status = _http_send(self._logger, data_to_send, self.service_endpoint_uri, self.send_timeout)
        if status is SUCCESS:
            self.consecutive_failures = 0
            return
        else:
            self.consecutive_failures = self.consecutive_failures + 1

        if self.consecutive_failures <= self.retry:
            for data in data_to_send:
                self._queue.put(data)


def _json_serialize_unknown(obj):
    """JSON serializer for objects not serializable by default json code.

    :param obj: the object to be serialized
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def _http_send(logger, data_to_send, service_endpoint_uri, send_timeout=10):
    """Replicate Application Insights SenderBase send method.

    :param logger: logger
    :param data_to_send: items to send
    :param service_endpoint_uri: endpoint
    :param send_timeout: timeout
    :return: SUCCESS/FAILURE
    """
    request_payload = json.dumps([a.write() for a in data_to_send], default=_json_serialize_unknown)

    content = bytearray(request_payload, "utf-8")
    begin = datetime.datetime.now()
    request = http_client_t.Request(
        service_endpoint_uri,
        content,
        {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    try:
        response = http_client_t.urlopen(request, timeout=send_timeout)
        logger.info("Sending %d bytes", len(content))
        status_code = response.getcode()
        if 200 <= status_code < 300:
            return SUCCESS
    except HTTPError as e:
        logger.error("Upload failed. HTTPError: %s", e)
        if e.getcode() == 400:
            return SUCCESS
    except OSError as e:  # socket timeout
        # stop retry during socket timeout
        logger.error("Upload failed. OSError: %s", e)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected exception: %s", e)
    finally:
        logger.info(
            "Finish uploading in %f seconds.",
            (datetime.datetime.now() - begin).total_seconds(),
        )

    return FAILURE
