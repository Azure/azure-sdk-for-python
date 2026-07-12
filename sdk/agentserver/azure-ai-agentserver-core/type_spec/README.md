# TypeSpec source for storage models

`main.tsp` is the formal TypeSpec contract for the Foundry State Storage wire
API (`/storage/state_stores/*`), companion to the prose spec
`foundry-state-storage-provider-spec.md` in `coreai-microsoft/foundrysdk_specs`.

It is the source of truth for the generated request/response model classes
under `azure/ai/agentserver/core/storage/_generated/` (`StateStore`,
`StateStoreItem`, `CreateStateStoreRequest`, etc.) — those files carry a
"Code generated ... do not edit" header and should only be changed by
re-running generation, not by hand.

## Why this isn't synced via `tsp-client` (yet)

Sibling packages like `azure-ai-agentserver-responses` generate models by
running `tsp-client sync` against a `tsp-location.yaml` pointing at a
directory under `Azure/azure-rest-api-specs`
(`specification/ai-foundry/data-plane/Foundry/src/...`). This contract does
not live there yet — there is no `state-stores` directory upstream. Until it
is published there, `main.tsp` is authored and compiled locally.

Once it lands upstream, replace `main.tsp` with a `tsp-location.yaml`
pointing at the new `specification/ai-foundry/data-plane/Foundry/src/state-stores`
directory and switch `make generate-models` back to the standard
`tsp-client sync` + compile flow, matching `azure-ai-agentserver-responses`.

## Regenerating models

From the package root:

```
make install-typespec-deps   # one-time: npm install pinned TypeSpec toolchain
make generate-models         # compile main.tsp -> azure/ai/agentserver/core/storage/_generated/
```

This runs `npx tsp compile main.tsp --emit @azure-tools/typespec-python`
(the same emitter used to generate `azure-ai-agentserver-responses`' models)
and copies the resulting `_models.py`, `_enums.py`, and `_utils/model_base.py`
into `_generated/`, discarding the generated client/operations code (this
package builds its own requests by hand in `_state.py`; only the model
classes are used).
