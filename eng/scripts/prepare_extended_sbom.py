import argparse
from email.parser import BytesParser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile

from packaging.utils import canonicalize_name
from packaging.version import Version

from ci_tools.functions import glob_packages


def prepare_discovery_inputs(repo_root: Path, artifact_directory: Path, output_directory: Path) -> None:
    requirements_path = output_directory / "requirements.txt"
    requirements_path.unlink(missing_ok=True)
    identities = {}
    for wheel in sorted(artifact_directory.rglob("*.whl")):
        with ZipFile(wheel) as archive:
            metadata_paths = [path for path in archive.namelist() if path.endswith(".dist-info/METADATA")]
            if len(metadata_paths) != 1:
                raise ValueError(f"Expected one package metadata file in {wheel}")
            metadata = BytesParser().parsebytes(archive.read(metadata_paths[0]))
        if not metadata["Name"] or not metadata["Version"]:
            raise ValueError(f"Package name or version missing in {wheel}")
        name = canonicalize_name(metadata["Name"])
        version = Version(metadata["Version"])
        if name in identities and identities[name] != version:
            raise ValueError(f"Multiple versions of {name} in the artifact: {identities[name]} and {version}")
        identities[name] = version
    if not identities:
        raise ValueError(f"No wheels found in {artifact_directory}")

    candidates = {}
    for root in (repo_root, repo_root / "eng" / "tools"):
        for directory in glob_packages("*", str(root)):
            path = Path(directory).resolve()
            candidates.setdefault(canonicalize_name(path.name), set()).add(path)

    requirements = []
    for name, version in sorted(identities.items()):
        sources = sorted(candidates.get(name, ()))
        if len(sources) != 1:
            raise ValueError(
                f"Expected one matching source project for artifact wheel {name}=={version}; found {sources}"
            )
        requirements.append(sources[0].as_uri())
        print(f"SBOM discovery input: {name}=={version} from {sources[0].relative_to(repo_root)}")

    with tempfile.TemporaryDirectory(prefix="extended-sbom-") as temporary:
        inputs = Path(temporary) / "requirements.txt"
        report = Path(temporary) / "metadata.json"
        inputs.write_text("\n".join(requirements) + "\n", encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--dry-run",
                "--ignore-installed",
                "--no-index",
                "--no-build-isolation",
                "--no-deps",
                "--report",
                str(report),
                "-r",
                str(inputs),
            ],
            check=True,
        )
        resolved = {
            canonicalize_name(item["metadata"]["name"]): Version(item["metadata"]["version"])
            for item in json.loads(report.read_text(encoding="utf-8"))["install"]
        }
        if resolved != identities:
            raise ValueError(f"Source package identities {resolved} do not match artifact wheels {identities}")

    # Local project inputs expose pyproject metadata without scanning tests or unrelated source trees.
    output_directory.mkdir(parents=True, exist_ok=True)
    requirements_path.write_text("\n".join(requirements) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Select extended SBOM discovery inputs from artifact wheels")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    prepare_discovery_inputs(
        args.repo_root.resolve(), args.artifact_directory.resolve(), args.output_directory.resolve()
    )


if __name__ == "__main__":
    main()
