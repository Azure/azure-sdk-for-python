from typing import Optional, List
from pydantic import BaseModel
import json

class ToolOverrides(BaseModel):
    """
    Optional overrides for tool metadata.

    Attributes:
        name (Optional[str]): The name of the tool.
        description (Optional[str]): The description of the tool.
        parameters (Optional[dict]): The parameters for the tool.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict] = None

class AgentToolDefinition(BaseModel):
    """
    Represents an agent tool definition.

    Attributes:
        type (str): The type of the tool.
        override (Optional[ToolOverrides]): Optional overrides for tool metadata.
    """
    type: str
    override: Optional[ToolOverrides] = None

class FunctionToolDefinition(AgentToolDefinition):
    """
    Represents a function tool definition.

    Attributes:
        type (str): The type of the tool, which is always 'function'.
        name (str): The name of the function.
        description (Optional[str]): The description of the function.
        parameters (Optional[dict]): JSON Schema describing the parameters, stored as raw JSON.
        strict (Optional[bool]): Indicates if the function is strict.
    """
    type: str = "function"
    name: str
    description: Optional[str] = None
    parameters: Optional[dict] = None
    strict: Optional[bool] = None

class BingGroundingToolDefinition(AgentToolDefinition):
    """
    Represents a Bing Grounding tool definition.

    Attributes:
        type (str): The type of the tool, which is always 'Microsoft.BingGrounding'.
        connection_name (str): The name of the connection.
    """
    type: str = "Microsoft.BingGrounding"
    connection_name: str

class CodeInterpreterToolDefinition(AgentToolDefinition):
    """
    Represents a Code Interpreter tool definition.

    Attributes:
        type (str): The type of the tool, which is always 'OpenAI.CodeInterpreter'.
        file_ids (Optional[List[str]]): A list of file IDs.
    """
    type: str = "OpenAI.CodeInterpreter"
    file_ids: Optional[List[str]] = None

class RankingOptions(BaseModel):
    """
    Represents ranking options.

    Attributes:
        score_threshold (float): The score threshold for ranking.
        ranker (Optional[str]): The ranker used for ranking.
    """
    score_threshold: float
    ranker: Optional[str] = None

class FileSearchToolDefinition(AgentToolDefinition):
    """
    Represents a File Search tool definition.

    Attributes:
        type (str): The type of the tool, which is always 'OpenAI.FileSearch'.
        max_num_results (Optional[int]): The maximum number of results.
        ranking_options (Optional[RankingOptions]): The ranking options.
        vector_store_id (Optional[str]): The ID of the vector store.
    """
    type: str = "OpenAI.FileSearch"
    max_num_results: Optional[int] = None
    ranking_options: Optional[RankingOptions] = None
    vector_store_id: Optional[str] = None

# class OpenApiToolDefinition(AgentToolDefinition):
#     """
#     Represents an OpenAPI tool definition.
#
#     Attributes:
#         type (str): The type of the tool, which is always 'OpenApi'.
#         name (str): The name of the tool.
#         description (Optional[str]): The description of the tool.
#         spec (BinaryData): The OpenAPI specification.
#         auth (OpenApiAuthDetails): The authentication details.
#     """
#     type: str = "OpenApi"
#     name: str
#     description: Optional[str] = None
#     spec: BinaryData
#     auth: OpenApiAuthDetails