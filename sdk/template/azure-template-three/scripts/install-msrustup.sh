#!/bin/sh
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Based on the version 7 bootstrap in Azure/azure-sdk-for-python#46851.
set -eu

for tool in uname curl jq unzip; do
    command -v "$tool" >/dev/null 2>&1 || {
        echo "install-msrustup requires $tool." >&2
        exit 1
    }
done

: "${MSRUSTUP_FEED_URL:?The pipeline must supply the Microsoft Rust toolchain feed.}"
if [ -z "${MSRUSTUP_ACCESS_TOKEN:-}" ] && [ -z "${MSRUSTUP_PAT:-}" ]; then
    echo "MSRUSTUP_ACCESS_TOKEN or MSRUSTUP_PAT must be set." >&2
    exit 1
fi

do_curl() {
    if [ -n "${MSRUSTUP_ACCESS_TOKEN:-}" ]; then
        curl -fsSL --retry 5 -H "Authorization: Bearer $MSRUSTUP_ACCESS_TOKEN" "$@"
    else
        curl -fsSL --retry 5 -u ":$MSRUSTUP_PAT" "$@"
    fi
}

case "$(uname -s)" in
    Linux) target_rest="-unknown-linux-gnu" ;;
    *) echo "This bootstrap is only used by Linux wheel containers." >&2; exit 1 ;;
esac
case "$(uname -m)" in
    x86_64) target_arch="x86_64" ;;
    aarch64 | arm64) target_arch="aarch64" ;;
    *) echo "Unsupported Microsoft Rust bootstrap architecture." >&2; exit 1 ;;
esac

package="rust.msrustup-${target_arch}${target_rest}"
response=$(do_curl "$MSRUSTUP_FEED_URL")
base=$(printf '%s' "$response" | jq -er '.resources[] | select(."@type" == "PackageBaseAddress/3.0.0") | .["@id"]')
response=$(do_curl "${base}${package}/index.json")
version=$(printf '%s' "$response" | jq -er '.versions[0]')
latest="${base}${package}/${version}/${package}.${version}.nupkg"

trap 'rm -f msrustup.zip' EXIT
echo "Installing msrustup ${version} for ${target_arch}${target_rest}."
do_curl "$latest" -o msrustup.zip
unzip -jqo msrustup.zip tools/msrustup
chmod +x msrustup
