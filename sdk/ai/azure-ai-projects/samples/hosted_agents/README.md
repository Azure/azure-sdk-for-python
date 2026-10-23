# Hosted agent samples

These samples create Python hosted agents from source archives or container
images, then demonstrate sessions, files, routines, and toolboxes.

## Python startup configuration

Each `HostedAgentDefinition` in this directory sets
`environment_variables={"PYTHONNOUSERSITE": "1", ...}` so the remote Python
interpreter starts without loading the user-site directory. The Python sample
image also sets `ENV PYTHONNOUSERSITE=1` in [assets/Dockerfile](assets/Dockerfile)
for container launches outside the hosted deployment definition.

This is customer-configured sample configuration, not a setting automatically
injected by the SDK or service. Configure it before the interpreter starts;
setting `os.environ` or loading a `.env` file inside `main.py` is too late for
Python startup. It disables Python user-site loading, not all code execution,
and does not configure other language runtimes. Create and deploy a new agent
version to apply it to an existing deployment; updating a local sample does
not change an already running version.

Install dependencies into a virtual environment, the container image's system
site-packages, or the source bundle's `packages/` directory as appropriate.
Do not depend on `pip install --user` or packages installed in the user-site
directory. Remote-build samples provide `requirements.txt`; bundled samples
provide their Linux-built dependencies under `packages/`, not the user site.

To build the Python image used by the image-deployment samples, run from this
directory:

```bash
docker build -f assets/Dockerfile -t <registry>/<repository>:<tag> assets/basic-agent
```

Publish the image to your registry and set `FOUNDRY_AGENT_CONTAINER_IMAGE` before
running either image-deployment sample. Keep the startup setting for Python
images; it has no effect on non-Python interpreters.

The [synchronous file sample](sample_sessions_files_upload_download.py) and
[asynchronous file sample](sample_sessions_files_upload_download_async.py)
include the same remote startup setting when creating their Python agent.
Their file upload and download operations do not configure interpreter startup.
