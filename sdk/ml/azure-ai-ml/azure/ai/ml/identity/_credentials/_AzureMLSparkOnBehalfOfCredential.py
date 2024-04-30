# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import functools
import os
from typing import Any, Optional

from azure.ai.ml.exceptions import MlException
from azure.core.pipeline.transport import HttpRequest

from .._internal.managed_identity_base import ManagedIdentityBase
from .._internal.managed_identity_client import ManagedIdentityClient


class _AzureMLSparkOnBehalfOfCredential(ManagedIdentityBase):
    def get_client(self, **kwargs: Any) -> Optional[ManagedIdentityClient]:
        client_args = _get_client_args(**kwargs)
        if client_args:
            return ManagedIdentityClient(**client_args)
        return None

    def get_unavailable_message(self) -> str:
        return "AzureML Spark On Behalf of credentials not available in this environment"


def _get_client_args(**kwargs: Any) -> Optional[dict]:
    # Override default settings if provided via arguments
    if len(kwargs) > 0:
        env_key_from_kwargs = [
            "AZUREML_SYNAPSE_CLUSTER_IDENTIFIER",
            "AZUREML_SYNAPSE_TOKEN_SERVICE_ENDPOINT",
            "AZUREML_RUN_ID",
            "AZUREML_RUN_TOKEN_EXPIRY",
        ]
        for env_key in env_key_from_kwargs:
            if env_key in kwargs:
                os.environ[env_key] = kwargs[env_key]
            else:
                msg = "Unable to initialize AzureMLHoboSparkOBOCredential due to invalid arguments"
                raise MlException(message=msg, no_personal_data_message=msg)
    else:
        from pyspark.sql import SparkSession  # cspell:disable-line # pylint: disable=import-error

        try:
            spark = SparkSession.builder.getOrCreate()
        except Exception as e:
            msg = "Fail to get spark session, please check if spark environment is set up."
            raise MlException(message=msg, no_personal_data_message=msg) from e

        spark_conf = spark.sparkContext.getConf()
        spark_conf_vars = {
            "AZUREML_SYNAPSE_CLUSTER_IDENTIFIER": "spark.synapse.clusteridentifier",
            "AZUREML_SYNAPSE_TOKEN_SERVICE_ENDPOINT": "spark.tokenServiceEndpoint",
        }
        for env_key, conf_key in spark_conf_vars.items():
            value = spark_conf.get(conf_key)
            if value:
                os.environ[env_key] = value

    token_service_endpoint = os.environ.get("AZUREML_SYNAPSE_TOKEN_SERVICE_ENDPOINT")
    obo_access_token = os.environ.get("AZUREML_OBO_CANARY_TOKEN")
    obo_endpoint = os.environ.get("AZUREML_OBO_USER_TOKEN_FOR_SPARK_RETRIEVAL_API", "getuseraccesstokenforspark")
    subscription_id = os.environ.get("AZUREML_ARM_SUBSCRIPTION")
    resource_group = os.environ.get("AZUREML_ARM_RESOURCEGROUP")
    workspace_name = os.environ.get("AZUREML_ARM_WORKSPACE_NAME")

    if not obo_access_token:
        return None

    # pylint: disable=line-too-long
    request_url_format = "https://{}/api/v1/proxy/obotoken/v1.0/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/{}"  # cspell:disable-line
    # pylint: enable=line-too-long

    url = request_url_format.format(
        token_service_endpoint, subscription_id, resource_group, workspace_name, obo_endpoint
    )

    return dict(
        kwargs,
        request_factory=functools.partial(_get_request, url),
    )


def _get_request(url: str, resource: Any) -> HttpRequest:
    obo_access_token = os.environ.get("AZUREML_OBO_CANARY_TOKEN")
    experiment_name = os.environ.get("AZUREML_ARM_PROJECT_NAME")
    run_id = os.environ.get("AZUREML_RUN_ID")
    oid = os.environ.get("OID")
    tid = os.environ.get("TID")
    obo_service_endpoint = os.environ.get("AZUREML_OBO_SERVICE_ENDPOINT")
    cluster_identifier = os.environ.get("AZUREML_SYNAPSE_CLUSTER_IDENTIFIER")

    request_body = {
        "oboToken": obo_access_token,
        "oid": oid,
        "tid": tid,
        "resource": resource,
        "experimentName": experiment_name,
        "runId": run_id,
    }
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "x-ms-proxy-host": obo_service_endpoint,
        "obo-access-token": obo_access_token,
        "x-ms-cluster-identifier": cluster_identifier,
    }
    request = HttpRequest(method="POST", url=url, headers=headers)
    request.set_json_body(request_body)
    return request
