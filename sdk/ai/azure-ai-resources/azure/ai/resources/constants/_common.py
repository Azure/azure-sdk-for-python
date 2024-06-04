# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


DEFAULT_OPEN_AI_CONNECTION_NAME = "Default_AzureOpenAI"
DEFAULT_CONTENT_SAFETY_CONNECTION_NAME = "Default_AzureAIContentSafety"
USER_AGENT_HEADER_KEY = "Client-User-Agent"

class AssetTypes:
    """An enumeration of values for the types of a data asset."""

    FILE = "file"
    """URI file data asset type."""
    FOLDER = "folder"
    """URI folder data asset type."""
    TABLE = "table"
    """Table data asset type."""

class IndexInputType(object):
    """An enumeration of values for the types of input data for an index."""
    GIT = "git"
    LOCAL = "local"
    AOAI = "aoai"
    """Azure OpenAI input data type."""


class IndexType(object):
    """An enumeration of values for the types of an index."""
    ACS = "acs"
    FAISS = "faiss"

class OperationScope:
    """An enumeration of values for the scope of an AIClient's operations.
    
    Some AIClient operations can be applied to either the client's AI resource
    or its project. For such operations, these values are used to determine that scope.
    """
    AI_RESOURCE = "ai_resource"
    PROJECT = "project"