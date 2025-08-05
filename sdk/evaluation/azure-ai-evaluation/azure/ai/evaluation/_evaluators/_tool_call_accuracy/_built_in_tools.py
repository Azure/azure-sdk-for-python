from typing import Dict, List, Optional

class BuiltInTools:
    """Tool definitions for built-in tools."""
    
    _BUILT_IN_TOOLS = {
        "azure_ai_search": {
            "type": "azure_ai_search",
            "description": "Enables agents to retrieve and ground responses in enterprise data indexed in Azure AI Search. This allows agents to provide accurate, context-aware answers based on internal knowledge bases.",
            "name": "azure_ai_search",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "A natural language query to an Azure AI Search index."
                    }
                }
            }
        },
        "bing_grounding": {
            "type": "bing_grounding",
            "description": "Allows agents to ground responses in real-time public web data. Useful for answering general questions, news, or trending topics.",
            "name": "bing_grounding",
            "parameters": {
                "type": "object",
                "properties": {
                    "requesturl": {
                        "type": "string",
                        "description": "Natural language search query sent to Bing."
                    }
                }
            }
        },
        "bing_custom_search": {
            "type": "bing_custom_search",
            "description": "Enables agents to retrieve content from a curated subset of websites, enhancing relevance and reducing noise from public web searches.",
            "name": "bing_custom_search",
            "parameters": {
                "type": "object",
                "properties": {
                    "requesturl": {
                        "type": "string",
                        "description": "Search queries, along with pre-configured site restrictions or domain filters."
                    }
                }
            }
        },
        "file_search": {
            "type": "file_search",
            "description": "Lets agents access user-uploaded files (PDFs, Word, Excel, etc.) for information retrieval. Grounding responses in these files ensures answers are personalized and accurate. A single call can return multiple results/files in the 'results' field.",
            "name": "file_search",
            "parameters": {
                "type": "object",
                "properties": {
                    "ranking_options": {
                        "type": "object",
                        "description": "The two options for ranking search results: ranker and score_threshold."
                    }
                }
            }
        },
        "sharepoint_grounding": {
            "type": "sharepoint_grounding",
            "description": "Allows agents to access and retrieve relevant content from Microsoft SharePoint document libraries, grounding responses in organizational knowledge.",
            "name": "sharepoint_grounding",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "A natural language query to search SharePoint content."
                    }
                }
            }
        },
        "code_interpreter": {
            "type": "code_interpreter",
            "description": "Enables agents to execute code snippets. Output of the tool can be empty but still be considered correct because the code executed successfully.",
            "name": "code_interpreter",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Code to be interpreted."
                    }
                }
            }
        },
        "fabric_dataagent": {
            "type": "fabric_dataagent",
            "description": "Empowers agents to query structured enterprise data using Microsoft Fabric datasets for real-time analysis or reporting.",
            "name": "fabric_dataagent",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Natural language targeting Fabric data sources"
                    }
                }
            }
        },
        "openapi": {
            "type": "openapi",
            "description": "Connects agents to external RESTful APIs using OpenAPI 3.0 specifications, enabling seamless access to third-party services.",
            "name": "openapi",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the function to call."
                    },
                    "arguments": {
                        "type": "string",
                        "description": "JSON string of the arguments to pass to the function."
                    }
                }
            }
        },
    }
    
    @classmethod
    def get_built_in_definition(cls, tool_name: str) -> Optional[Dict]:
        """Get the definition for the built-in tool."""
        return cls._BUILT_IN_TOOLS.get(tool_name)
    
    @classmethod
    def get_needed_built_in_definitions(cls, tool_calls: List[Dict]) -> List[Dict]:
        """Extract tool definitions needed for the given built-in tool calls."""
        needed_definitions = []
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                tool_type = tool_call.get("type")
                if tool_type in cls._BUILT_IN_TOOLS:
                    built_in_def = cls._BUILT_IN_TOOLS[tool_type]
                    if built_in_def not in needed_definitions:
                        needed_definitions.append(built_in_def)
        
        return needed_definitions