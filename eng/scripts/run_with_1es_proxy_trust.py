# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Run a pipeline command with the CA supplied by Windows or Linux 1ES network isolation."""

import argparse
import os
import shlex
import ssl
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import certifi


def proxy_trust_required() -> bool:
    return (
        sys.platform in ("win32", "linux")
        and os.environ.get("TF_BUILD", "").lower() == "true"
        and bool(os.environ.get("1ESNI_CONFIG_PATH"))
        and bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"))
    )


def configure_linux_containers(environment: dict[str, str], bundle: Path) -> None:
    from cibuildwheel.oci_container import OCIContainerEngineConfig

    engine = OCIContainerEngineConfig.from_config_string(
        environment.get("CIBW_CONTAINER_ENGINE_LINUX", environment.get("CIBW_CONTAINER_ENGINE", "docker"))
    )
    # Mount the bundle at the same path so SSL_CERT_FILE works on the host and in containers.
    create_args = list(engine.create_args)
    create_args.append(f"--volume={bundle}:{bundle}:ro")
    for name in (
        "SSL_CERT_FILE",
        "HTTPS_PROXY",
        "HTTP_PROXY",
        "NO_PROXY",
        "https_proxy",
        "http_proxy",
        "no_proxy",
    ):
        if name in environment:
            create_args.append(f"--env={name}")

    environment["CIBW_CONTAINER_ENGINE_LINUX"] = (
        f"{engine.name}; create_args: {shlex.join(create_args)}; "
        f"disable_host_mount: {str(engine.disable_host_mount).lower()}"
    )


def create_proxy_environment(bundle: Path) -> dict[str, str]:
    # Require the infrastructure-provided CA handoff; never infer a platform-specific path.
    proxy_ca = os.environ.get("NODE_EXTRA_CA_CERTS")
    if not proxy_ca:
        raise RuntimeError("1ES proxy trust requires the CA path supplied in NODE_EXTRA_CA_CERTS.")
    baseline_ca = os.environ.get("SSL_CERT_FILE", certifi.where())

    print("Preparing pipeline command TLS trust with the 1ES network-isolation proxy CA.", flush=True)
    with bundle.open("wb") as combined:
        for certificate_file in (baseline_ca, proxy_ca):
            ssl.create_default_context(cafile=certificate_file)
            combined.write(Path(certificate_file).read_bytes())
            combined.write(b"\n")
    ssl.create_default_context(cafile=str(bundle))

    environment = os.environ.copy()
    environment["SSL_CERT_FILE"] = str(bundle)
    if sys.platform == "linux":
        configure_linux_containers(environment, bundle)
    return environment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command and arguments to run without a shell.")
    args = parser.parse_args()
    if not args.command:
        parser.error("a command is required")

    # Bare Python lookup can bypass a Windows launcher-based virtual environment.
    if args.command[0] in ("python", "python.exe"):
        args.command[0] = sys.executable

    if not proxy_trust_required():
        return subprocess.run(args.command, env=None, check=False).returncode

    with TemporaryDirectory(prefix="pipeline-proxy-ca-") as directory:
        bundle = Path(directory).resolve() / "ca-bundle.pem"
        environment = create_proxy_environment(bundle)
        return subprocess.run(args.command, env=environment, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
