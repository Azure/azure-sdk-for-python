#!/bin/sh
# Point cargo inside the manylinux container at the authenticated pipeline feed.
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

# Cargo reads the registry index and credentials from the environment, but
# crates.io source replacement must be specified in a configuration file.
cat > "$CARGO_CONFIG_HOME/config.toml" <<EOF
[source.crates-io]
replace-with = "$REGISTRY_NAME"

[net]
git-fetch-with-cli = true
EOF

echo "Replaced the crates-io source with '$REGISTRY_NAME' in $CARGO_CONFIG_HOME/config.toml"
