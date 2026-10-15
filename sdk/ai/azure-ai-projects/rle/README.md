# RLE development SDK beta registry

This is the development counterpart of the `rle-releases` registry. Public
distribution uses the `Azure/azure-sdk-for-python` branch `rle-dev-releases`.
Publishing is a separate, human-owned step; pushing this SDK PR does not publish
an artifact to the public repository.

Publish these files under `sdk/ai/azure-ai-projects/rle`, matching public PR #49488:

- `install_rle_sdk.py`
- `registry.json`
- `wheels/2.7.0b2/azure_ai_projects-2.7.0b2-py3-none-any.whl`

The registry pins the wheel checksum. This build uses `2.7.0b2`, following
`2.7.0b1` in the existing `rle-releases` registry. Subsequent development builds
should increment the beta number and update the registry checksum. The installer
also explicitly reinstalls the verified wheel if the installed version matches.

For a development installation:

```bash
curl --fail --location \
  https://raw.githubusercontent.com/Azure/azure-sdk-for-python/rle-dev-releases/sdk/ai/azure-ai-projects/rle/install_rle_sdk.py \
  --output install_rle_sdk.py
python install_rle_sdk.py --version 2.7.0b2
```

Use `--requirements runtime-requirements.txt` to install command-job dependencies
alongside the SDK. The installer does not add environment-authoring extras.

For reproducible command-job images, download the installer and registry from
an approved immutable public commit instead of a moving branch. Pass that
registry URL with `--manifest`. Its wheel URL should also use the artifact's
immutable commit, retaining the wheel SHA-256. A moving PR branch can expose
private code, require authentication, or change during a build; it is not the
anonymous command-job distribution endpoint.

The recipe's package metadata must use the same wheel URL and checksum.
Otherwise a later `pip install` of the recipe can replace the SDK selected by
the installer. Public publication and download/hash verification must complete
before updating those dependency pins.
