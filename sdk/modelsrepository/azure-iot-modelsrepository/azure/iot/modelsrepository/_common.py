# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import platform
from enum import Enum
from ._version import VERSION

USER_AGENT = "azsdk-python-modelsrepository/{pkg_version} Python/{py_version} ({platform})".format(
    pkg_version=VERSION, py_version=(platform.python_version()), platform=platform.platform()
)
DEFAULT_API_VERSION = "2021-02-11"


# Public constants exposed to consumers
DEFAULT_LOCATION = "https://devicemodels.azure.com"
METADATA_FILE = "metadata.json"

# Standard strings
CLIENT_INIT_MSG = "Client configured for repository location \"{0}\"."
DISCOVERED_DEPENDENCIES = "Discovered dependencies \"{0}\"."
ERROR_FETCHING_MODEL_CONTENT = (
    "Model file \"{0}\" not found or not accessible in target repository. Fallback to non-expanded"
    "model content and will determine dependencies for this model manually."
)
FAILURE_PROCESSING_REPOSITORY_METADATA = (
    "Unable to fetch or process repository metadata file. Repository assumed to not have expanded "
    "models. The client will fetch non-expanded model content and determine dependencies manually."
)
FETCHER_INIT_MSG = "Repository Location identified as {0}. Client session initialized with {1}."
FETCHING_MODEL_CONTENT = "Attempting to fetch model content from \"{0}\"."
GENERIC_GET_MODELS_ERROR = "Failure handling \"{0}\"."
INCORRECT_DTMI_CASING = "Fetched model has incorrect DTMI casing. Expected \"{0}\", parsed \"{1}\"."
INVALID_DEPEDENCY_MODE = "Dependency mode must be enabled or disabled."
INVALID_DTMI_FORMAT = "Invalid DTMI format \"{0}\"."
PROCESSING_DTMI = "Processing DTMI \"{0}\". "
SKIPPING_PRE_PROCESSED_DTMI = "Already processed DTMI \"{0}\". Skipping."


class DependencyMode(Enum):
    """
    Dependency Mode options.
    """

    disabled = "disabled"
    enabled = "enabled"


class ModelProperties(Enum):
    """
    DTMI Model properties for parsing models in Model Query.
    """

    id = "@id"
    type = "@type"
    extends = "extends"
    contents = "contents"
    schema = "schema"


class ModelType(Enum):
    """
    Possible DTMI model types.
    """

    interface = "Interface"
    component = "Component"


class RemoteProtocolType(Enum):
    """
    Remote protocol for web URL.
    """

    http = "http"
    https = "https"
