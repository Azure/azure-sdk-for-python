# TypeSpec Client Generator MCP Server

This is a Model Context Protocol (MCP) server that wraps the [@azure-tools/typespec-client-generator-cli](https://www.npmjs.com/package/@azure-tools/typespec-client-generator-cli) npm package commands.

## Prerequisites

- Python
- Node.js and npm/npx

## Available Tools

This MCP server provides the following tools:

- `init`: Initialize a client library directory using a tspconfig.yaml file.
- `init_local`: Initialize a client library directory using a path to a local tspconfig.yaml file.

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