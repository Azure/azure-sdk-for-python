# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


DEFAULT_OPEN_AI_CONNECTION_NAME = "Default_AzureOpenAI"
DEFAULT_CONTENT_SAFETY_CONNECTION_NAME = "Default_AzureAIContentSafety"
USER_AGENT_HEADER_KEY = "Client-User-Agent"

class AssetTypes:
    """AssetTypes is an enumeration of values for the asset types of a data.

    Asset types are used to identify the type of an asset. An asset can be a file, folder, table
    """

    FILE = "file"
    """URI file data asset type."""
    FOLDER = "folder"
    """URI folder data asset type."""
    TABLE = "table"
    """Table data asset type."""

class IndexInputType(object):
    GIT = "git"
    LOCAL = "local"
    AOAI = "aoai"


class IndexType(object):
    ACS = "acs"
    FAISS = "faiss"

class OperationScope:
    """Some AI Client Operations can be applied to either the client's AI resource
    or its project. For such operations, this is used to determine that scope.
    """
    AI_RESOURCE = "ai_resource"
    PROJECT = "project"