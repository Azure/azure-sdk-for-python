#!/bin/sh
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
set -eu

index="${CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_INDEX:-}"
if [ -z "$index" ]; then
    echo "No Cargo registry index supplied; using crates.io."
    exit 0
fi
if [ -z "${CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_TOKEN:-}" ]; then
    echo "The configured Cargo feed requires an authentication token." >&2
    exit 1
fi

cargo_home="${CARGO_HOME:-$HOME/.cargo}"
mkdir -p "$cargo_home"
config="$cargo_home/config.toml"
if [ -e "$config" ]; then
    echo "Refusing to overwrite the Cargo configuration: $config" >&2
    exit 1
fi

cat > "$config" <<EOF
[registries.azure-sdk-for-rust-public]
index = "$index"

[source.crates-io]
replace-with = "azure-sdk-for-rust-public"

[net]
git-fetch-with-cli = true
EOF

echo "Configured Cargo source replacement in $config."
