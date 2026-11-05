# Queued V3 development wheel

This standalone artifact is the previously tested
`azure-ai-projects==2.7.0b7.dev20261104+queuedv3.3` wheel, republished without
rebuilding or changing its bytes.

* Size: 601096 bytes.
* SHA-256: `ee4630608daeda2a539e3a2f98f2da1dc90e89a577c61dc23edaff4ac6afbf87`.
* Original immutable artifact commit: `9d53899d688ac00cf239d5c25d01c37dd44f6116`
  in `swatisinghvi99/azure-sdk-for-python`.
* Build source: `673607acb7d782b4f7ce8b21d138464713f83016` in
  `sujit-kamireddy/azure-sdk-for-python`; see [provenance](provenance.json).

The source-only SDK PR was merged into the source fork as
`4f82d3c33e5e55614aeb167bce2ff1980ceba64e`. That is not an upstream source merge.
This distribution does not include source-tree changes or obsolete `.1`/`.2`
development wheels.

The optional `get_rollout_client(..., protocol_version="v3")` selects queued V3
only, without fallback. Omission preserves legacy defaults. The wheel retains
fine-tuning identity support, bounded durable delivery/recovery, per-submission
expiry checks and the bounded opaque job-ID fix.

This is a development artifact, not an approved registry release or PyPI
publication. Registry/latest, the installer and all existing artifacts are
unchanged. Pin an immutable public wheel URL with the SHA-256 above.

The unchanged wheel previously passed 226 offline rollout tests against source
and its public-installed package. Publication checks verify the exact wheel and
provenance bytes, metadata, ZIP/RECORD hashes, and recorded source contents.
No image builds, cloud jobs, deployment, permissions changes or merging are
performed by this publication.
