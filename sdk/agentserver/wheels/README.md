# Checked-in preview wheels

This directory ships the three `azure-ai-agentserver-*` packages as
locally-built wheels so the `resilient-agent-demo` docker image can
`pip install /tmp/wheels/*.whl` without needing to publish each
preview to PyPI.

| Wheel | Source |
|-------|--------|
| `azure_ai_agentserver_core-*.whl` | `sdk/agentserver/azure-ai-agentserver-core` |
| `azure_ai_agentserver_invocations-*.whl` | `sdk/agentserver/azure-ai-agentserver-invocations` |
| `azure_ai_agentserver_responses-*.whl` | `sdk/agentserver/azure-ai-agentserver-responses` |

## Consumption

The `resilient-agent-demo/build.sh` copies these wheels into the docker
build context (`samples/resilient-agent-demo/src/.../wheels/`). The
sample's `Dockerfile` then runs `pip install --no-cache-dir /tmp/wheels/*.whl`
to pull them in.

Devs do NOT need to rebuild these — they're checked in.

## Refreshing (maintainer-only)

After source changes to any of the three packages, run:

```bash
sdk/agentserver/wheels/build-wheels.sh
git add sdk/agentserver/wheels/*.whl
git commit
```

The script removes stale `*.whl` files and re-builds at the version
in each package's `_version.py`. No version bump is needed for
unreleased `bN` previews — the same filename is overwritten with the
new content.
