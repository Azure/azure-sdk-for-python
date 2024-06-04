# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import json
import shutil
from pathlib import Path
from typing import Iterable, Optional

from azure.ai.ml.constants._common import DefaultOpenEncoding
from azure.ai.ml.entities import OnlineEndpoint
from azure.ai.ml.entities._load_functions import load_online_endpoint


class EndpointStub:
    """EndpointStub is a class for representing local endpoints which do not have deployments created under them yet.

    To maintain a catalog of local endpoints, it writes a yaml file with the endpoint specification to the user's
    machine in an idempotent, well-known location.
    """

    def create_or_update(self, endpoint: OnlineEndpoint) -> OnlineEndpoint:
        """Create or update a local endpoint.

        :param OnlineEndpoint endpoint: OnlineEndpoint entity to create or update.
        :return: The provided endpoint
        :rtype: OnlineEndpoint
        """
        self._create_endpoint_cache(endpoint=endpoint)
        return endpoint

    def get(self, endpoint_name: str) -> Optional[OnlineEndpoint]:
        """Get a local endpoint.

        :param str endpoint_name: Name of local endpoint to get.
        :return: The specified Online Endpoint
        :rtype: Optional[Endpoint]
        """
        endpoint_path = self._get_endpoint_cache_file(endpoint_name=endpoint_name)
        if endpoint_path.exists():
            return load_online_endpoint(source=endpoint_path)
        return None

    def list(self) -> Iterable[Path]:
        """List all local endpoints.

        :return: An iterable of paths to endpoints
        :rtype: Iterable[Path]
        """
        endpoints = []
        azureml_dir = self._get_inferencing_cache_dir()
        for endpoint_file in azureml_dir.glob("*/*.json"):
            endpoints.append(endpoint_file)
        return endpoints

    def delete(self, endpoint_name: str):
        """Delete a local endpoint.

        :param str endpoint_name: Name of local endpoint to delete.
        """
        build_directory = self._get_build_directory(endpoint_name=endpoint_name)
        shutil.rmtree(build_directory)

    def invoke(self):
        """Invoke a local endpoint.

        For an EndpointStub, it cannot invoke, so we return a helper message.

        :return: Invocation result
        :rtype: str
        """
        return (
            "This local endpoint does not have any deployments, so it cannot be invoked."
            "Please use 'az ml online-deployment create --local' before invoking."
        )

    def _create_endpoint_cache(self, endpoint: OnlineEndpoint) -> Path:
        """Create or update a local endpoint cache.

        :param OnlineEndpoint endpoint: OnlineEndpoint entity to create or update.
        :return: The endpoint cache path
        :rtype: Path
        """
        endpoint_cache_path = self._get_endpoint_cache_file(endpoint_name=str(endpoint.name))
        endpoint_metadata = json.dumps(endpoint.dump())
        endpoint_cache_path.write_text(endpoint_metadata, encoding=DefaultOpenEncoding.WRITE)
        return endpoint_cache_path

    def _get_endpoint_cache_file(self, endpoint_name: str) -> Path:
        """Get a local endpoint cache Path. Idempotent.

        :param str endpoint_name: Name of local endpoint to get local cache.
        :return: path to cached endpoint file.
        :rtype: Path
        """
        build_directory = self._create_build_directory(endpoint_name=endpoint_name)
        return Path(build_directory, f"{endpoint_name}.json")

    def _create_build_directory(self, endpoint_name: str) -> Path:
        """Create or update a local endpoint build directory.

        :param str endpoint_name: Name of local endpoint to get local directory.
        :return: path to endpoint build directory.
        :rtype: Path
        """
        build_directory = self._get_build_directory(endpoint_name=endpoint_name)
        build_directory.mkdir(parents=True, exist_ok=True)
        return build_directory

    def _get_build_directory(self, endpoint_name: str) -> Path:
        """Get a local endpoint build directory. Idempotent.

        :param str endpoint_name: Name of local endpoint to get local directory.
        :return: path to endpoint build directory.
        :rtype: Path
        """
        return Path(self._get_inferencing_cache_dir(), endpoint_name)

    @classmethod
    def _get_inferencing_cache_dir(cls) -> Path:
        """Get a local inferencing directory. Idempotent.

        :return: path to local inferencing cache directory.
        :rtype: Path
        """
        return Path(Path.home(), ".azureml", "inferencing")
