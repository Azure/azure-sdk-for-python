# Archived pre-parity public-SDK tests

The historical preview oracle is identified by
[../eng/generation/reference.json](../eng/generation/reference.json). The active
SDK uses TypeSpec generation plus supported Python hooks, with explicit reviewed
changes recorded in [../eng/generation/review-deltas.json](../eng/generation/review-deltas.json).
It is not a byte-identical copy of that oracle or the earlier public-only
implementation. See [../GENERATION.md](../GENERATION.md).

These Python files preserve superseded public-only tests and are **not part of
active test discovery or passing-test totals**. Several depend on obsolete model
or helper shapes. Their exclusion does not prove an issue fixed or still open.
Applicable heartbeat-shutdown, credential security, POST-retry, and raw
request-ID polling regressions are now covered by active tests; those fixes are
not deferred. Only the change from automatic heartbeat startup to opt-in-only
startup remains an unimplemented lifecycle decision.

Use the current contracts when adapting any remaining applicable regression;
do not restore obsolete API expectations merely to reactivate an archived file.
The complete prior implementation and tests remain in Git commit
`8ebc1ea5c9d0682edfa857388c0cabc863c6ab70`.

The immutable 48-file oracle, including its 19 upstream test files, is unchanged.
Active tests retain upstream coverage with specifically recorded adaptations
and additions. The compatibility gate checks exact inventories and hashes;
unrecorded changes or missing upstream tests fail rather than being normalized
away. Historical test and wheel results are not validation of the current SDK.
