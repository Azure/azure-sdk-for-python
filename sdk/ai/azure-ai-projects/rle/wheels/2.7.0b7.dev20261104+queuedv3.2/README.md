# Queued V3 development artifact: per-submission expiry fix

Version `2.7.0b7.dev20261104+queuedv3.2` fixes connection lifetime checks
between queued submissions. A backpressured send can cross credential or
rotation expiry; the SDK now rotates before preparing or marking the next
unsent rollout submitted. Submitted rollouts attach with their original IDs
and received cursors. Deadlines, admission permits and no-execute-replay
semantics are unchanged.

SHA-256: `6a368b26ea32d8611a35cb76ae42ef93bcb618a52a56b25a1c94f87a6e9d401d`.
Size: 600792 bytes. See [provenance](provenance.json) for source/build identity.
This is a standalone development-only artifact, not an approved registry
release or PyPI publication. The previous wheel is not overwritten.

```python
async with project_client.rle.get_rollout_client(
    environment_name,
    environment_version,
    job_id,
    protocol_version="v3",
    finetune_credential=finetune_credential,
) as session:
    result = await session.execute_rollout(task=task, policy=policy)
```

Omission preserves legacy v2/v1 defaults. Explicit V3 never falls back.
The source and exact installed wheel each passed 198 offline rollout tests,
including `test_expiry_during_send_rotates_before_next_submission`.
Two independent builds were byte-identical; all 62 Python modules matched
source, and wheel metadata/RECORD hashes passed integrity checks. Targeted
Python 3.10 transport type and 120-column Black checks passed.

Pin an immutable public commit URL with the SHA-256 above; no GitHub credentials
are required. The artifact contains public SDK source only. The SDK source
review remains separate: this distribution does not modify Python source on
`rle-releases`. Registry/latest, installer and older artifacts remain unchanged.

Image rebuild/selection is still needed. Full package release gates and
cloud/model tests were not run; nothing was deployed or merged.
