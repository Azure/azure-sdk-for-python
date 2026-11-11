# Reproducible SDK generation

This package is generated from the public Microsoft Foundry TypeSpec sources
with maintained Python customization hooks. Changes to generated code belong
in TypeSpec or the supported hooks, not in generated modules.

## Current source pin and review validation

[tsp-location.yaml](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/tsp-location.yaml)
records the public specification repository, exact commit, entrypoint, and
additional source directories.
[eng/generation/provenance.json](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-finetuningsessions/eng/generation/provenance.json)
records current public source, toolchain, generated-output, and runtime hashes.
Those records describe reproducibility, not live-service certification or
release approval.

## Toolchain

The repository's shared `eng/emitter-package.json` and
`eng/emitter-package-lock.json` are authoritative. Exact copies are archived
under this package's `eng/generation/` directory for standalone verification.
Do not upgrade a package-local dependency independently of the shared pair.

The Python generator's isolated environment uses the requirements in
`eng/generation/requirements.txt`. Those are build tools, not runtime package
dependencies. Restore them only in the generation environment.

## Generation check

From the package directory, use the existing verifier with local public
specification and SDK checkouts and an installation of the pinned tools:

```powershell
python scripts\verify_generation.py `
  --spec-repo <specification-checkout> `
  --sdk-repo <sdk-checkout> `
  --toolchain <pinned-toolchain-directory>
```

The verifier:

1. Checks source and toolchain fingerprints against the committed provenance.
2. Seeds only the maintained customization modules listed in the provenance.
3. Emits twice into clean temporary outputs with packaging generation disabled.
4. Compares every generated entry and every assembled runtime file.
5. Rejects missing, extra, modified, or nondeterministic output.

Only checkout line-ending differences are normalized. The verifier does not
rewrite source, update package metadata, install dependencies, or change Git
state. Refresh the source pin and provenance together after reviewing an
intentional generation change.

## Validation and packaging

Run the package's existing tests, type checks, formatting, spelling, and
documentation checks after changing source or hooks. Validate the public API
snapshot and inspect actual wheel/source-distribution contents before release.
The package README and changelog both appear in its PyPI long description.

Distribution inputs are explicitly allowlisted in `MANIFEST.in`.
Customer documentation, public API metadata, public generation inputs, and
runtime modules are included. Source distributions also include the active
public test sources required by SDK validation; wheels do not install them.
Historical review notes, private-source audit records, archived tests, and
unrelated maintainer utilities are not release inputs.

Public documentation must not expose internal project names, deployment
architecture, capacity routing, private repository links, or validation
diaries. Supported legacy protocol identifiers may remain in implementation
code for compatibility; do not rename a working wire value as a prose cleanup.
