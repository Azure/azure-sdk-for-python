# Azure SDK Validation Tools MCP Server

This is a Model Context Protocol (MCP) server that provides access to various validation and testing tools used in the Azure SDK for Python repository.

## Prerequisites

- Python 3.8 or higher

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

## Running the Server

Start the MCP server with:

```bash
python main.py
```

## Available Tools

This MCP server provides the following validation tools:

### tox

Run tox environments.

```python
result = client.tox(
    package_path="path/to/package",
    environment="pylint",  # Optional, e.g., 'pylint', 'mypy', etc.
    config_file="path/to/tox.ini"  # Optional
)
```

## Tool Response Format

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

## Example Usage

Here's an example of how to use the validation tools from Python:

```python
from mcp.client import MCPClient

client = MCPClient("http://localhost:8080")

# Run a specific tox environment
result = client.tox(
    package_path="sdk/core/azure-core",
    environment="pylint",
    config_file="eng/tox/tox.ini"
)

print(result)
```
