# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import json
import shutil
from pathlib import Path
from azure.ai.ml.entities import OnlineEndpoint
from typing import Iterable
from azure.ai.ml.entities._load_functions import load_online_endpoint


class EndpointStub:
    """EndpointStub is a class for representing local endpoints which do not have deployments created under them yet.
    To maintain a catalog of local endpoints, it writes a yaml file with the endpoint specification to the user's machine
    in an idempotent, well-known location.
    """

    def create_or_update(self, endpoint: OnlineEndpoint):
        """Create or update a local endpoint.

        :param endpoint OnlineEndpoint: OnlineEndpoint entity to create or update.
        """
        self._create_endpoint_cache(endpoint=endpoint)
        return endpoint

    def get(self, endpoint_name: str):
        """Get a local endpoint.

        :param endpoint_name str: Name of local endpoint to get.
        """
        endpoint_path = self._get_endpoint_cache_file(endpoint_name=endpoint_name)
        if endpoint_path.exists():
            return load_online_endpoint(path=endpoint_path)
        return None

    def list(self) -> Iterable[Path]:
        """List all local endpoints."""
        endpoints = []
        azureml_dir = self._get_inferencing_cache_dir()
        for endpoint_file in azureml_dir.glob("*/*.json"):
            endpoints.append(endpoint_file)
        return endpoints

    def delete(self, endpoint_name: str):
        """Delete a local endpoint.

        :param endpoint_name str: Name of local endpoint to delete.
        """
        build_directory = self._get_build_directory(endpoint_name=endpoint_name)
        shutil.rmtree(build_directory)

    def invoke(self):
        """Invoke a local endpoint. For an EndpointStub, it cannot invoke, so we return a helper message."""
        return "This local endpoint does not have any deployments, so it cannot be invoked. Please use 'az ml online-deployment create --local' before invoking."

    def _create_endpoint_cache(self, endpoint: OnlineEndpoint):
        """Create or update a local endpoint cache.

        :param endpoint OnlineEndpoint: OnlineEndpoint entity to create or update.
        """
        endpoint_cache_path = self._get_endpoint_cache_file(endpoint_name=endpoint.name)
        endpoint_metadata = json.dumps(endpoint.dump())
        endpoint_cache_path.write_text(endpoint_metadata)
        return endpoint_cache_path

    def _get_endpoint_cache_file(self, endpoint_name: str) -> Path:
        """Get a local endpoint cache Path. Idempotent.

        :param endpoint_name str: Name of local endpoint to get local cache.
        :returns Path: path to cached endpoint file.
        """
        build_directory = self._create_build_directory(endpoint_name=endpoint_name)
        return Path(build_directory, f"{endpoint_name}.json")

    def _create_build_directory(self, endpoint_name: str) -> Path:
        """Create or update a local endpoint build directory.

        :param endpoint_name str: Name of local endpoint to get local directory.
        :returns Path: path to endpoint build directory.
        """
        build_directory = self._get_build_directory(endpoint_name=endpoint_name)
        build_directory.mkdir(parents=True, exist_ok=True)
        return build_directory

    def _get_build_directory(self, endpoint_name: str) -> Path:
        """Get a local endpoint build directory. Idempotent.

        :param endpoint_name str: Name of local endpoint to get local directory.
        :returns Path: path to endpoint build directory.
        """
        return Path(self._get_inferencing_cache_dir(), endpoint_name)

    def _get_inferencing_cache_dir(self) -> Path:
        """Get a local inferencing directory. Idempotent.

        :returns Path: path to local inferencing cache directory.
        """
        return Path(Path.home(), ".azureml", "inferencing")
