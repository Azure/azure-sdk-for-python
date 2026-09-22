# Archived pre-parity public-SDK tests

The active preview baseline preserves the tested Loom customer API and behavior
identified by [../loom-source.json](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/loom-source.json), using TypeSpec generation
plus supported Python hooks. It is not the earlier public-only contract or the
exact old internal file layout. See [../GENERATION.md](https://github.com/Azure/azure-sdk-for-python/blob/feature/finetuning-sessions-sdk/sdk/ai/azure-ai-finetuningsessions/GENERATION.md).

The Python files in this directory preserve the previous public-only tests for
the next review stage. They are deliberately **not part of the active baseline
test suite**. Several require models or helpers that do not exist in the Loom
snapshot. Do not interpret their exclusion as proof that the reviewed issues
are fixed. The independently reproduced heartbeat shutdown regression has now
been reactivated under the normal tests directory with the reviewed fix; the
remaining historical tests still assume superseded public-only API shapes.

Reintroduce each applicable test with its corresponding separately reviewed fix
after baseline parity and TypeSpec reconciliation. The complete prior public
implementation and tests are also retained in Git commit
`8ebc1ea5c9d0682edfa857388c0cabc863c6ab70`.

The copied upstream tests in `tests/` remain unchanged apart from the approved
package/import spelling and run normally. The compatibility gate rejects
missing, added, or modified files in that upstream test inventory.
