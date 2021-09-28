# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import platform
from ._version import VERSION
from enum import Enum

USER_AGENT = "azsdk-python-modelsrepository/{pkg_version} Python/{py_version} ({platform})".format(
    pkg_version=VERSION, py_version=(platform.python_version()), platform=platform.platform()
)
DEFAULT_API_VERSION = "2021-02-11"


# Public constants exposed to consumers
DEFAULT_LOCATION = "https://devicemodels.azure.com"
METADATA_FILE = "metadata.json"

# Standard strings TODO figure out best way to allow inputs in string
GenericGetModelsError = "Failure handling \"{0}\"."
InvalidDtmiFormat = "Invalid DTMI format \"{0}\"."
ClientInitWithFetcher = "Client session {0} initialized with {1} content fetcher."
ProcessingDtmi = "Processing DTMI \"{0}\". "
SkippingPreProcessedDtmi = "Already processed DTMI \"{0}\". Skipping."
DiscoveredDependencies = "Discovered dependencies \"{0}\"."
FetchingModelContent = "Attempting to fetch model content from \"{0}\"."
ErrorFetchingModelContent = "Model file \"{0}\" not found or not accessible in target repository."
FailureProcessingRepositoryMetadata = "Unable to fetch or process repository metadata file."
IncorrectDtmiCasing = "Fetched model has incorrect DTMI casing. Expected \"{0}\", parsed \"{1}\"."


class DependencyModeType(Enum):
    """
    Dependency Mode options.
    """

    disabled = "disabled"
    enabled = "enabled"


class RemoteProtocolType(Enum):
    """
    Remote protocol for web URL.
    """

    http = "http"
    https = "https"

class ModelType(Enum):
    """
    Possible DTMI modely types.
    """

    interface = "Interface"
    component = "Component"


class ModelProperties(Enum):
    """
    DTMI Model properties for parsing models in Model Query.
    """

    id = "@id"
    type = "@type"
    extends = "extends"
    contents = "contents"
    schema = "schema"
