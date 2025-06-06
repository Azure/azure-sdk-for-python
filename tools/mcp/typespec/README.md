# TypeSpec Client Generator MCP Server

This is a Model Context Protocol (MCP) server that wraps the [@azure-tools/typespec-client-generator-cli](https://www.npmjs.com/package/@azure-tools/typespec-client-generator-cli) npm package commands.

## Prerequisites

- Python 3.10 or higher
- Node.js and npm/npx
- uv

## Available Tools

This MCP server provides the following tools:

- `init`: Initialize a client library directory using a tspconfig.yaml file.
- `init_local`: Initialize a client library directory using a path to a local tspconfig.yaml file.
