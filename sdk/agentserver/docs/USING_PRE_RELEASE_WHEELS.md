# Using pre-release agentserver wheels

The `azure-ai-agentserver-*` packages are not yet published to PyPI. Until
they are, consume them as local wheels built from this branch.

## 1. Build the wheels

From the repo root:

```bash
sdk/agentserver/scripts/build-wheels.sh
```

This produces:

```
sdk/agentserver/wheels/
├── azure_ai_agentserver_core-<version>-py3-none-any.whl
└── azure_ai_agentserver_invocations-<version>-py3-none-any.whl
```

The `wheels/` directory is git-ignored — re-run the script after every
pull to refresh.

## 2. Consume the wheels in your project

### Option A — install into a virtual env (local dev)

```bash
pip install path/to/sdk/agentserver/wheels/azure_ai_agentserver_core-*.whl
pip install path/to/sdk/agentserver/wheels/azure_ai_agentserver_invocations-*.whl
```

### Option B — bundle into a container image (hosted agent)

Copy the wheels into your project, install them in the Dockerfile *before*
your `requirements.txt`:

```dockerfile
# Copy pre-built agentserver wheels (built via
# sdk/agentserver/scripts/build-wheels.sh in the durable-tasks branch)
COPY wheels/azure_ai_agentserver_core-*.whl /tmp/wheels/
COPY wheels/azure_ai_agentserver_invocations-*.whl /tmp/wheels/

RUN pip install --no-cache-dir /tmp/wheels/*.whl

# Then install the rest of your app dependencies
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

Useful when you want `pip install -r requirements.txt` to pull pre-release
agentserver alongside other deps. Relative paths work too if `pip` is
invoked from the right working directory.

## 3. Rebuilding after a code change

After pulling the latest from the `feature/agentserver-durable-tasks`
branch (or making a local edit), re-run:

```bash
sdk/agentserver/scripts/build-wheels.sh
pip install --force-reinstall --no-deps sdk/agentserver/wheels/*.whl
```

The `--no-deps` keeps the install fast — only the agentserver packages
themselves change between rebuilds.

## When this doc goes away

Once the agentserver packages ship to PyPI, replace local wheel installs
with the standard `pip install azure-ai-agentserver-core azure-ai-agentserver-invocations`.
This doc is interim guidance only.
