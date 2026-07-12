# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Integration layer for optional Fabric mirror serving."""

# pylint: disable=protected-access

import importlib
from typing import Any, Dict, List, Optional

from .exceptions import MirrorServingNotAvailableError

_REQUIRED_CONFIG_KEYS = {
    "server": ["server", "fabric_server"],
    "database": ["database", "fabric_database"],
}


def _lazy_import_mapper():
    """Dynamically import mapper package only when needed.

    :returns: Module handle to azure_cosmos_fabric_mapper.sdk_hook.contract.
    :rtype: module
    :raises ~azure.cosmos.exceptions.MirrorServingNotAvailableError: If package is not installed.
    """
    try:
        return importlib.import_module("azure.cosmos.fabric_mapper.sdk_hook.contract")
    except ImportError as exc:
        raise MirrorServingNotAvailableError() from exc


def _validate_mirror_config(mirror_config: Dict[str, Any]) -> None:
    """Validate that required keys are present in mirror_config.

    :param dict mirror_config: The mirror configuration dictionary to validate.
    :raises ValueError: If required keys are missing.
    """
    for logical_key, accepted_names in _REQUIRED_CONFIG_KEYS.items():
        if not any(name in mirror_config for name in accepted_names):
            raise ValueError(
                f"mirror_config is missing required key '{logical_key}'. "
                f"Provide one of: {accepted_names}. "
                f"Required keys: server (or fabric_server), database (or fabric_database)."
            )


def _get_config_value(mirror_config: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Get the first matching key from mirror_config.

    :param dict mirror_config: The mirror configuration dictionary.
    :param str keys: One or more key names to look up in order.
    :keyword default: Default value if no key is found.
    :returns: The value of the first matching key, or default.
    :rtype: Any
    """
    for key in keys:
        if key in mirror_config:
            return mirror_config[key]
    return default


def execute_mirrored_query(
    query: str,
    parameters: Optional[List[Dict[str, Any]]],
    mirror_config: Dict[str, Any],
    cached_client: Optional[Any] = None,
) -> tuple:
    """Execute query against Fabric mirror using mapper package.

    :param str query: Cosmos SQL query text.
    :param parameters: List of parameter dicts with 'name' and 'value' keys.
    :type parameters: Optional[list[dict[str, Any]]]
    :param dict mirror_config: Dict with server, database, and optional credential, fabric_table, fabric_schema.
    :param cached_client: Optional cached driver client to reuse connections.
    :type cached_client: Optional[Any]
    :returns: Tuple of (results list, driver_client) — caller can cache the driver_client.
    :rtype: tuple
    :raises ~azure.cosmos.exceptions.MirrorServingNotAvailableError: If mapper package not installed.
    """
    _validate_mirror_config(mirror_config)
    contract = _lazy_import_mapper()

    mapper = importlib.import_module("azure.cosmos.fabric_mapper")
    credentials_module = importlib.import_module("azure.cosmos.fabric_mapper.credentials")
    driver_module = importlib.import_module("azure.cosmos.fabric_mapper.driver")

    server = _get_config_value(mirror_config, "server", "fabric_server")
    database = _get_config_value(mirror_config, "database", "fabric_database")
    table = _get_config_value(mirror_config, "table_override", "fabric_table", default="")
    schema = _get_config_value(mirror_config, "fabric_schema", default="dbo")

    config = mapper.MirrorServingConfiguration(
        fabric_server=server,
        fabric_database=database,
        fabric_table=table,
        fabric_schema=schema,
    )

    request = contract.MirroredQueryRequest(
        query=query,
        parameters=parameters,
    )

    # Use user-provided credential or fall back to default
    user_credential = mirror_config.get("credential")
    credentials = (
        user_credential
        if user_credential is not None
        else credentials_module.DefaultAzureSqlCredential()
    )

    created_driver = cached_client is None
    driver_client = cached_client or driver_module.get_driver_client(config=config, credentials=credentials)

    try:
        results = contract.run_mirrored_query(
            request=request,
            config=config,
            credentials=credentials,
            driver=driver_client,
        )
    except BaseException as query_error:
        if created_driver:
            try:
                driver_client.close()
            except Exception as close_error:  # pylint: disable=broad-except
                raise query_error from close_error
        raise

    return results, driver_client


def execute_mirrored_query_with_cache(
    connection: Any,
    query: str,
    parameters: Optional[List[Dict[str, Any]]],
    mirror_config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Execute a mirrored query while coordinating the cached driver lifecycle.

    :param connection: Cosmos connection that owns the cached mirror driver.
    :type connection: Any
    :param str query: Cosmos SQL query text.
    :param parameters: Optional query parameters.
    :type parameters: Optional[list[dict[str, Any]]]
    :param dict mirror_config: Fabric mirror configuration.
    :returns: Query results.
    :rtype: list[dict[str, Any]]
    """
    with connection._mirror_driver_lock:
        if connection._mirror_driver_closed:
            raise ValueError("Cannot execute a mirror query after CosmosClient has been closed.")

        cached_client = connection._mirror_driver_client
        try:
            results, driver_client = execute_mirrored_query(
                query=query,
                parameters=parameters,
                mirror_config=mirror_config,
                cached_client=cached_client,
            )
        except BaseException as query_error:
            if cached_client is not None:
                connection._mirror_driver_client = None
                try:
                    cached_client.close()
                except Exception as close_error:  # pylint: disable=broad-except
                    raise query_error from close_error
            raise

        connection._mirror_driver_client = driver_client
        return results


def close_mirror_driver(connection: Any) -> None:
    """Close the cached mirror driver after all active mirror queries finish.

    :param connection: Cosmos connection that owns the cached mirror driver.
    :type connection: Any
    """
    with connection._mirror_driver_lock:
        connection._mirror_driver_closed = True
        mirror_driver = connection._mirror_driver_client
        connection._mirror_driver_client = None
        if mirror_driver is not None:
            mirror_driver.close()
