# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import concurrent.futures
import logging
import time
from concurrent.futures import Future
from typing import Any, Callable, Union

from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource, is_registry_id_for_resource
from azure.ai.ml._utils._logger_utils import initialize_logger_info
from azure.ai.ml.constants._common import ARM_ID_PREFIX, AzureMLResourceType, LROConfigurations
from azure.ai.ml.entities import BatchDeployment
from azure.ai.ml.entities._assets._artifacts.code import Code
from azure.ai.ml.entities._deployment.deployment import Deployment
from azure.ai.ml.operations._operation_orchestrator import OperationOrchestrator
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.core.polling import LROPoller
from azure.core.rest import HttpResponse
from azure.mgmt.core.exceptions import ARMErrorFormat

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="")


def get_duration(start_time: float) -> None:
    """Calculates the duration of the Long running operation took to finish

    :param start_time: Start time
    :type start_time: float
    """
    end_time = time.time()
    duration = divmod(int(round(end_time - start_time)), 60)
    module_logger.warning("(%sm %ss)\n", duration[0], duration[1])


def polling_wait(
    poller: Union[LROPoller, Future],
    message: str = None,
    start_time: float = None,
    is_local=False,
    timeout=LROConfigurations.POLLING_TIMEOUT,
) -> Any:
    """Print out status while polling and time of operation once completed.

    :param poller: An poller which will return status update via function done().
    :type poller: Union[LROPoller, concurrent.futures.Future]
    :param (str, optional) message: Message to print out before starting operation write-out.
    :param (float, optional) start_time: Start time of operation.
    :param (bool, optional) is_local: If poller is for a local endpoint, so the timeout is removed.
    :param (int, optional) timeout: New value to overwrite the default timeout.
    """
    module_logger.warning("%s", message)
    if is_local:
        # We removed timeout on local endpoints in case it takes a long time
        # to pull image or install conda env.

        # We want user to be able to see that.

        while not poller.done():
            module_logger.warning(".")
            time.sleep(LROConfigurations.SLEEP_TIME)
    else:
        poller.result(timeout=timeout)

    if poller.done():
        module_logger.warning("Done ")
    else:
        module_logger.warning("Timeout waiting for long running operation")

    if start_time:
        get_duration(start_time)


def local_endpoint_polling_wrapper(func: Callable, message: str, **kwargs) -> Any:
    """Wrapper for polling local endpoint operations.

    :param Callable func: Name of the endpoint.
    :param str message: Message to print out before starting operation write-out.
    :param dict kwargs: kwargs to be passed to the func
    :return: The type returned by Func
    """
    pool = concurrent.futures.ThreadPoolExecutor()
    start_time = time.time()
    event = pool.submit(func, **kwargs)
    polling_wait(poller=event, start_time=start_time, message=message, is_local=True)
    return event.result()


def validate_response(response: HttpResponse) -> None:
    """Validates the response of POST requests, throws on error

    :param HttpResponse response: the response of a POST requests
    :raises Exception: Raised when response is not json serializable
    :raises HttpResponseError: Raised when the response signals that an error occurred
    """
    r_json = {}

    if response.status_code not in [200, 201]:
        # We need to check for an empty response body or catch the exception raised.
        # It is possible the server responded with a 204 No Content response, and json parsing fails.
        if response.status_code != 204:
            try:
                r_json = response.json()
            except ValueError:
                # exception is not in the json format
                raise Exception(response.content.decode("utf-8"))
        failure_msg = r_json.get("error", {}).get("message", response)
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
        }
        map_error(status_code=response.status_code, response=response, error_map=error_map)
        raise HttpResponseError(response=response, message=failure_msg, error_format=ARMErrorFormat)


def upload_dependencies(deployment: Deployment, orchestrators: OperationOrchestrator) -> None:
    """Upload code, dependency, model dependencies. For BatchDeployment only
    register compute.

    :param Deployment deployment: Endpoint deployment object.
    :param OperationOrchestrator orchestrators: Operation Orchestrator.
    """

    module_logger.debug("Uploading the dependencies for deployment %s", deployment.name)

    # Create a code asset if code is not already an ARM ID
    if (
        deployment.code_configuration
        and not is_ARM_id_for_resource(deployment.code_configuration.code, AzureMLResourceType.CODE)
        and not is_registry_id_for_resource(deployment.code_configuration.code)
    ):
        if deployment.code_configuration.code.startswith(ARM_ID_PREFIX):
            deployment.code_configuration.code = orchestrators.get_asset_arm_id(
                deployment.code_configuration.code[len(ARM_ID_PREFIX) :],
                azureml_type=AzureMLResourceType.CODE,
            )
        else:
            deployment.code_configuration.code = orchestrators.get_asset_arm_id(
                Code(base_path=deployment._base_path, path=deployment.code_configuration.code),
                azureml_type=AzureMLResourceType.CODE,
            )

    if not is_registry_id_for_resource(deployment.environment):
        deployment.environment = (
            orchestrators.get_asset_arm_id(deployment.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
            if deployment.environment
            else None
        )
    if not is_registry_id_for_resource(deployment.model):
        deployment.model = (
            orchestrators.get_asset_arm_id(deployment.model, azureml_type=AzureMLResourceType.MODEL)
            if deployment.model
            else None
        )
    if isinstance(deployment, BatchDeployment) and deployment.compute:
        deployment.compute = orchestrators.get_asset_arm_id(
            deployment.compute, azureml_type=AzureMLResourceType.COMPUTE
        )
