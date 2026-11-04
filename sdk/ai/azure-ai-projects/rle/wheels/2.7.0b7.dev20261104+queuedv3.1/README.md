# Queued V3 development artifact

This is the exact hash-verified `azure-ai-projects` development wheel
`2.7.0b7.dev20261104+queuedv3.1`, not an official release or PyPI publication.
It is a standalone, explicitly selected artifact and is **not added to the
approved release registry**. The registry, `latest`, installer and all existing
wheel versions/checksums are unchanged.

SHA-256:

```text
1cca2b75a5f2fbfa864584bf7f0f830098bf4fe13519cc4e1a39b3bd60a9ea8e
```

The [provenance record](provenance.json) identifies the source commit, verified
baseline wheel and offline validation. This artifact contains public Python SDK
source only, not service source, tests, credentials or environment files.
The SDK implementation is reviewed separately; adding the artifact does not
change the source tree on `rle-releases` or qualify the service for production.

## Supported opt-in

```python
async with project_client.rle.get_rollout_client(
    environment_name=environment_name,
    environment_version=environment_version,
    job_id=job_id,
    protocol_version="v3",
    finetune_credential=finetune_credential,
) as session:
    result = await session.execute_rollout(task=task, policy=policy)
```

Omitting `protocol_version` preserves legacy v2/v1 defaults. Explicit V3 offers
only `rle.execute-rollout.v3` and verifies selection, without legacy fallback.
The optional fine-tuning credential preserves the consumed b7 identity behavior.
Queued acceptance is not completion; the SDK awaits durable terminal delivery
and uses original-ID attachment recovery without automatic execute replay.

## Validation and consumption

The exact wheel passed 197 offline rollout tests in an isolated installation;
the same 197 source tests passed. Repository wheel validation and targeted
Python 3.10 transport type checks passed. All 62 packaged Python modules matched
the recorded source commit, and two independent builds produced identical bytes.
No live model/cloud execution, deployment, permissions changes or merging was
performed.

Pin a full immutable public commit URL and the SHA-256 above rather than a
mutable branch or an unverified download. A development consumer must rebuild
and select its training image after changing the pin. SDK packaging does not
enable server gates, create worker capacity or perform live qualification.
