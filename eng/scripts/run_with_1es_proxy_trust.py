# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Run a pipeline command with the CA supplied by Windows or Linux 1ES network isolation."""

import argparse
import os
import shlex
import ssl
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Optional

import certifi


def configure_linux_containers(environment: dict[str, str], bundle: Path) -> None:
    from cibuildwheel.oci_container import OCIContainerEngineConfig

    engine = OCIContainerEngineConfig.from_config_string(
        environment.get("CIBW_CONTAINER_ENGINE_LINUX", environment.get("CIBW_CONTAINER_ENGINE", "docker"))
    )
    forwarded = (
        "SSL_CERT_FILE",
        "HTTPS_PROXY",
        "HTTP_PROXY",
        "NO_PROXY",
        "https_proxy",
        "http_proxy",
        "no_proxy",
    )
    # A host SSL_CERT_FILE is otherwise absent and inaccessible inside cibuildwheel containers.
    create_args = [
        *engine.create_args,
        f"--volume={bundle}:{bundle}:ro",
        *(f"--env={name}" for name in forwarded if name in environment),
    ]
    environment["CIBW_CONTAINER_ENGINE_LINUX"] = (
        f"{engine.name}; create_args: {shlex.join(create_args)}; "
        f"disable_host_mount: {str(engine.disable_host_mount).lower()}"
    )


@contextmanager
def proxy_environment() -> Iterator[Optional[dict[str, str]]]:
    if (
        sys.platform not in ("win32", "linux")
        or os.environ.get("TF_BUILD", "").lower() != "true"
        or not os.environ.get("1ESNI_CONFIG_PATH")
        or not (os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"))
    ):
        yield None
        return

    # Require the infrastructure-provided CA handoff; never infer a platform-specific path.
    proxy_ca = os.environ.get("NODE_EXTRA_CA_CERTS")
    if not proxy_ca:
        raise RuntimeError("1ES proxy trust requires the CA path supplied in NODE_EXTRA_CA_CERTS.")
    baseline_ca = os.environ.get("SSL_CERT_FILE", certifi.where())

    print("Preparing pipeline command TLS trust with the 1ES network-isolation proxy CA.", flush=True)
    with TemporaryDirectory(prefix="pipeline-proxy-ca-") as directory:
        bundle = Path(directory).resolve() / "ca-bundle.pem"
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
        yield environment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command and arguments to run without a shell.")
    args = parser.parse_args()
    if not args.command:
        parser.error("a command is required")

    # Bare Python lookup can bypass a Windows launcher-based virtual environment.
    if args.command[0] in ("python", "python.exe"):
        args.command[0] = sys.executable

    with proxy_environment() as environment:
        return subprocess.run(args.command, env=environment, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
