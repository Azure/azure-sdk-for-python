# Patching Generated Python SDK Code

Handwritten patches (including `_patch.py`) extend generated SDK code without editing generated files directly. Follow the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html) and the applicable generator's customization guidance; the [AutoRest Python customization guide](https://github.com/Azure/autorest.python/blob/main/docs/customizations.md) describes patching mechanics.

## Before Adding or Changing a Patch

Apply this checklist to handwritten patches and customizations of generated Python SDK code, whether made manually or through customization tools:

1. **Identify generation inputs.** Record the generating tool and resolved version, service spec path and revision, configuration/options, and generation command. For TypeSpec, inspect `tsp-location.yaml`, `tspconfig.yaml`, and applicable emitter dependency/version records; for legacy AutoRest, inspect its generation configuration and generator version. Do not assume the current repository dependency version produced the affected code.
2. **Investigate the source of the behavior.** Distinguish an incorrect service spec/configuration from an emitter/generator defect or intentional SDK customization. When practical, use a minimal spec reproduction or regenerate with the identified inputs and inspect the unpatched output to establish evidence. Prefer correcting spec/configuration and regenerating, or fixing/reporting generator-wide defects in the responsible tool's upstream repository, instead of masking them in one SDK.
3. **Justify legitimate customizations.** Service-specific behavior and backward-compatibility patches remain valid when intentional. Explain why the behavior belongs in the SDK's handwritten customization rather than the spec/configuration or generator.
4. **Track temporary generator workarounds.** For a confirmed emitter/generator bug, reference an existing upstream issue when available; otherwise document an explicit plan to report it. Add a regression test demonstrating the affected behavior and verifying the workaround, and state the removal/regeneration condition (for example, regenerate with a fixed generator version and remove the patch once the unpatched output passes the test).
5. **Document the diagnosis.** Include the inputs, expected versus actual behavior, reproduction/regeneration commands and results, and patch rationale in the PR description or nearby customization documentation. If investigation cannot be completed, record the blocker, what remains unverified, and the follow-up needed; do not claim an emitter/generator bug was ruled out without evidence.

This checklist is contributor and agent guidance, not automated enforcement.
