#!/bin/sh
# Point cargo at an Azure Artifacts feed that mirrors crates.io.
#
# Run by the cibuildwheel `before-all` hook inside the manylinux container. Build
# agents are network isolated and cannot reach index.crates.io, so cargo has to
# resolve through the feed instead.
#
# Cargo reads `registries.<name>.index` and its credentials from the environment,
# but it ignores `source.crates-io.replace-with` set that way, so the replacement
# has to live in a config file. The index and the token stay in the environment
# and are never written to disk here.
#
# Does nothing when no index was forwarded, so a developer building locally with
# direct crates.io access is unaffected.
set -eu

REGISTRY_NAME=azure-sdk-for-rust-public
INDEX="${CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_INDEX:-}"

if [ -z "$INDEX" ]; then
  echo "No cargo registry index forwarded, leaving crates.io source unchanged."
  exit 0
fi

if [ -z "${CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_TOKEN:-}" ]; then
  echo "Cargo registry index is set but its token is missing; the feed requires authentication." >&2
  exit 1
fi

CARGO_CONFIG_HOME="${CARGO_HOME:-$HOME/.cargo}"
mkdir -p "$CARGO_CONFIG_HOME"

# git-fetch-with-cli makes cargo shell out to git for git dependencies rather
# than using its built in client, so those fetches use the container's git
# configuration and credentials.
cat > "$CARGO_CONFIG_HOME/config.toml" <<EOF
[source.crates-io]
replace-with = "$REGISTRY_NAME"

[net]
git-fetch-with-cli = true
EOF

echo "Replaced the crates-io source with '$REGISTRY_NAME' in $CARGO_CONFIG_HOME/config.toml"
