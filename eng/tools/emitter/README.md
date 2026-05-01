# TypeSpec Python Emitter

This directory holds files related to the TypeSpec Python emitter (`@azure-tools/typespec-python` and `@typespec/http-client-python`).

## Contents

- **`gen/`** — Auto-generated Python SDK test code produced by the emitter.
  These files are regenerated automatically by the [typespec-python-regenerate](https://github.com/Azure/azure-sdk-for-python/blob/main/.github/workflows/typespec-python-regenerate.yml) workflow whenever the emitter version in `eng/emitter-package.json` is updated.

> **Do not edit files in `gen/` by hand.** They will be overwritten on the next regeneration.
