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
        from azure_cosmos_fabric_mapper.sdk_hook import contract  # pylint: disable=import-error
        return contract
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

    from azure_cosmos_fabric_mapper import MirrorServingConfiguration  # pylint: disable=import-error
    from azure_cosmos_fabric_mapper.credentials import DefaultAzureSqlCredential  # pylint: disable=import-error
    from azure_cosmos_fabric_mapper.driver import get_driver_client  # pylint: disable=import-error

    server = _get_config_value(mirror_config, "server", "fabric_server")
    database = _get_config_value(mirror_config, "database", "fabric_database")
    table = _get_config_value(mirror_config, "table_override", "fabric_table", default="")
    schema = _get_config_value(mirror_config, "fabric_schema", default=database)

    config = MirrorServingConfiguration(
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
    credentials = user_credential if user_credential is not None else DefaultAzureSqlCredential()

    # Reuse cached driver client if available, otherwise create new one
    driver_client = cached_client or get_driver_client(config=config, credentials=credentials)

    results = contract.run_mirrored_query(
        request=request,
        config=config,
        credentials=credentials,
        driver=driver_client,
    )

    return results, driver_client
