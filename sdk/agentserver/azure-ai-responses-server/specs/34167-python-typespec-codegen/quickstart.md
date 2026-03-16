# Quickstart: Python TypeSpec Code Generation

## Prerequisites

- **Node.js** v18+ ([download](https://nodejs.org/))
- **Python** 3.10+
- **GNU Make** (included with most Linux/macOS; on Windows install a GNU Make distribution such as GnuWin32 Make)

## Windows PowerShell

On Windows, this Makefile can be run directly from PowerShell after installing GNU Make, Node.js, and Python. Git Bash or WSL are no longer required.

## First-Time Setup

Install the TypeSpec CLI tooling and sync TypeSpec source definitions:

```bash
make install-typespec-deps
```

This installs `tsp-client` globally via npm and runs `tsp-client sync` to fetch TypeSpec source files from `Azure/azure-rest-api-specs` into `type_spec/TempTypeSpecFiles/`.

## Generate Python Models

```bash
make generate-models
```

Generated Python model files appear in `azure/ai/responses/server/_generated/`.

## Clean Generated Output

```bash
make clean
```

Removes the entire `azure/ai/responses/server/_generated/` directory.

## Clean Regeneration

```bash
make clean generate-models
```

## Verify Generated Models

After generation, validate that the output passes project linting and type-checking:

```bash
ruff check azure/ai/responses/server/_generated/
mypy azure/ai/responses/server/_generated/
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `tsp-client: command not found` | Run `make install-typespec-deps` |
| `node: command not found` | Install Node.js v18+ from https://nodejs.org/ |
| TypeSpec compile errors | Check `type_spec/*.tsp` for syntax issues; run `tsp-client generate` directly for verbose output |
| Stale generated files | Run `make clean generate-models` for a fresh generation |
