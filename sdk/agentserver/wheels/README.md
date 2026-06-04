# Using the `@task` private-preview wheels

This directory ships the pre-release `azure-ai-agentserver-*` wheels
containing the **private-preview `@task` durable-task primitive**. The
wheels are checked in — there's nothing to build before you consume them.

## What ships where

| Package | Source | Includes `@task`? |
|---|---|---|
| `azure-ai-agentserver-core` on PyPI (stable) | `pip install azure-ai-agentserver-core` | ❌ No |
| `azure-ai-agentserver-invocations` on PyPI (stable) | `pip install azure-ai-agentserver-invocations` | ❌ No |
| `azure-ai-agentserver-core` **2.0.0b6 wheel** in this directory | `azure_ai_agentserver_core-2.0.0b6-py3-none-any.whl` | ✅ Yes |
| `azure-ai-agentserver-invocations` **1.0.0b5 wheel** in this directory | `azure_ai_agentserver_invocations-1.0.0b5-py3-none-any.whl` | ✅ Yes (matched pair) |

The `azure-ai-agentserver-*` packages are published on PyPI at stable
versions. **The `@task` durable-task primitive itself is in private
preview** and ships *only* as the pre-release wheels in this directory.
Until `@task` reaches GA, the stable PyPI version of the package will
not contain `azure.ai.agentserver.core.durable` — installing from PyPI
gives you the surrounding agentserver framework, not the durable-task
API.

## Consume the wheels in your project

### Option A — install into a virtual env (local dev)

```bash
# Copy or clone, then point pip at the local wheel files
pip install --upgrade \
    /path/to/sdk/agentserver/wheels/azure_ai_agentserver_core-*.whl \
    /path/to/sdk/agentserver/wheels/azure_ai_agentserver_invocations-*.whl
```

`--upgrade` is important if you already have the stable PyPI version
installed — without it, pip will refuse to "downgrade" past the version
heuristics.

### Option B — bundle into a container image (hosted agent)

Copy the wheels into your project and install them in the Dockerfile
*before* the rest of your `requirements.txt`:

```dockerfile
# Bundle the @task preview wheels (copied from sdk/agentserver/wheels/
# in the Azure/azure-sdk-for-python feature/agentserver-durable-tasks
# branch). Install them ahead of requirements.txt so the rest of your
# deps don't pull a non-preview version off PyPI.
COPY wheels/azure_ai_agentserver_core-*.whl /tmp/wheels/
COPY wheels/azure_ai_agentserver_invocations-*.whl /tmp/wheels/
RUN pip install --no-cache-dir /tmp/wheels/*.whl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

And in `requirements.txt`, **do not** list `azure-ai-agentserver-*`
(they're already installed from the local wheels above).

### Option C — pin in `requirements.txt` for local install

```
file:///abs/path/to/sdk/agentserver/wheels/azure_ai_agentserver_core-2.0.0b6-py3-none-any.whl
file:///abs/path/to/sdk/agentserver/wheels/azure_ai_agentserver_invocations-1.0.0b5-py3-none-any.whl
```

Relative paths work too when `pip` is invoked from the right working
directory.

## When this doc goes away

Once `@task` reaches GA and the durable-task primitive is included in
the regular PyPI release of `azure-ai-agentserver-core`, replace local
wheel installs with the standard
`pip install azure-ai-agentserver-core azure-ai-agentserver-invocations`
and delete this directory.

---

## For maintainers — refreshing the checked-in wheels

Whenever the agentserver core or invocations source changes on this
branch, rebuild the wheels and commit them:

```bash
./build-wheels.sh           # from this directory, or
sdk/agentserver/wheels/build-wheels.sh   # from the repo root

git add *.whl
git commit -m "[agentserver] refresh @task preview wheels"
```

The build script removes only the existing `*.whl` files (it leaves
this `README.md` and the script itself intact). Wheel files are binary
so each rebuild produces a fresh SHA; `git diff` won't be
human-readable, but committing them keeps the preview surface portable.
