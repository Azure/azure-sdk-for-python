# TypeSpec Client Generator MCP Server

This is a Model Context Protocol (MCP) server that wraps the [@azure-tools/typespec-client-generator-cli](https://www.npmjs.com/package/@azure-tools/typespec-client-generator-cli) npm package commands.

## Prerequisites

- Python 3.8 or higher
- Node.js and npm/npx

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate
```

3. Install the dependencies:
```bash
pip install -e .
```

4. Install the TypeSpec client generator CLI:
```bash
npm install -g @azure-tools/typespec-client-generator-cli
```

## Running the Server

Start the MCP server with:

```bash
python main.py
```

## Available Tools

This MCP server provides the following tools:

- `init`: Initialize a client library directory using a tspconfig.yaml file
- `update`: Look for a tsp-location.yaml file to sync a TypeSpec project and generate a client library
- `sync`: Sync a TypeSpec project with parameters specified in tsp-location.yaml
- `generate`: Generate a client library from a TypeSpec project
- `convert`: Convert an existing swagger specification to a TypeSpec project
- `compare`: Compare two Swagger definitions to identify relevant differences
- `sort_swagger`: Sort an existing swagger specification to match TypeSpec generated swagger order
- `generate_config_files`: Generate default configuration files used by tsp-client

## Example Usage

The MCP server can be used with any MCP client. Here's an example of how to use the `generate` tool from Python:

```python
from mcp.client import MCPClient

client = MCPClient("http://localhost:8080")

result = client.generate(
    project_directory="path/to/typespec/project",
    output_directory="path/to/output",
    language="python"
)

print(result)
```

## Error Handling

Each tool returns a response with the following structure:

```json
{
    "success": true/false,
    "stdout": "standard output from the command",
    "stderr": "standard error from the command",
    "code": 0,  // return code, 0 means success
    "error": "error message if any"
}
```

Check the `success` field to determine if the command was successful.