#!/bin/sh

# Originally from https://aka.ms/install-msrustup.sh
# Version 7
# This script is expected to be copied into any build system that needs to install the internal Rust toolchain, if
# that system cannot use an ADO pipeline and the Rust installer pipeline task.
# Updates to this script will be avoided if possible, but if it stops working in your environment, please check the above
# source location in case of any changes.

# Downloads msrustup from Azure Artifacts.
# Requires MSRUSTUP_ACCESS_TOKEN or MSRUSTUP_PAT environment variables to be set with a token.
# See https://aka.ms/rust for more information.

command -v uname >/dev/null 2>&1 || { echo >&2 "install-msrustup requires uname to detect host."; exit 1; }
command -v curl >/dev/null 2>&1 || { echo >&2 "install-msrustup requires curl to download msrustup."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo >&2 "install-msrustup requires jq to parse Azure Artifact response."; exit 1; }
command -v unzip >/dev/null 2>&1 || { echo >&2 "install-msrustup requires unzip to unzip msrustup."; exit 1; }

if [ -z "$MSRUSTUP_ACCESS_TOKEN" ] && [ -z "$MSRUSTUP_PAT" ]; then
    if $(command -v azureauth >/dev/null 2>&1); then
        MSRUSTUP_ACCESS_TOKEN=$(azureauth ado token)
    elif $(command -v azureauth.exe >/dev/null 2>&1); then
        MSRUSTUP_ACCESS_TOKEN=$(azureauth.exe ado token)
    else
        echo "MSRUSTUP_ACCESS_TOKEN or MSRUSTUP_PAT must be set or azureauth must be present."
        exit 1
    fi
fi

if [ -z "$MSRUSTUP_ACCESS_TOKEN" ]; then
    accessMethod=pat
else
    accessMethod=token
fi

if [ -z "$MSRUSTUP_FEED_URL" ]; then
    MSRUSTUP_FEED_URL='https://devdiv.pkgs.visualstudio.com/DevDiv/_packaging/Rust.Sdk%40Release/nuget/v3/index.json'
fi

# Now that we've tested for missing required variables, treat unset variables as an error.
set -eu

cleanup() {
  rm -f msrustup.zip
}
trap cleanup EXIT

do_curl() {
    if [ "$accessMethod" = "token" ]; then
        curl -sSfLH "Authorization: Bearer $MSRUSTUP_ACCESS_TOKEN" --retry 5 $@
    else
        curl -sSfLu :$MSRUSTUP_PAT --retry 5 $@
    fi
}

target_arch=''
target_rest=''

# We intentionally use the msvc host toolchain for variations of Windows (CYGWIN, MINGW, etc)
# since no other Windows host toolchain is supported.
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     target_rest="-unknown-linux-gnu";;
    Darwin*)    target_rest="-apple-darwin";;
    CYGWIN*)    target_rest="-pc-windows-msvc";;
    MINGW*)     target_rest="-pc-windows-msvc";;
    MSYS_NT*)   target_rest="-pc-windows-msvc";;
    *)          { echo "host environment could not be determined: ${unameOut}"; exit 1; }
esac

# Detect x86_64 or aarch64 (Apple devices report as "arm64", Linux as "aarch64" usually).
arch="$(uname -m)"
case "${arch}" in
    x86_64*)   target_arch="x86_64";;
    aarch64*)  target_arch="aarch64";;
    arm64*)    target_arch="aarch64";;
    *)         { echo "unknown host arch: ${arch}"; exit 1; }
esac

echo "Host is ${target_arch}${target_rest}"
package="rust.msrustup-${target_arch}${target_rest}"

response=$(do_curl $MSRUSTUP_FEED_URL)
base=$(echo $response | jq -r '.resources[] | select(."@type"=="PackageBaseAddress/3.0.0") | .["@id"]')
version=$(do_curl "$base$package/index.json" | jq -r '.versions[0]')
latest="${base}${package}/$version/$package.$version.nupkg"

echo "Downloading msrustup $version from $latest"
do_curl "$latest" -o msrustup.zip

if [ "$target_rest" = "-pc-windows-msvc" ]; then
    unzip -jqo msrustup.zip tools/msrustup.exe
else
    unzip -jqo msrustup.zip tools/msrustup
    chmod +x msrustup
fi