import argparse
import json
import pathlib
import subprocess

import yaml

from extract_apiview_metadata import extract_metadata


def update_package_info(metadata_path: pathlib.Path, package_info_path: pathlib.Path) -> None:
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8-sig"))
    api_hash = metadata.get("apiMdSha256") if isinstance(metadata, dict) else None
    if not isinstance(api_hash, str) or not api_hash:
        raise ValueError(f"apiMdSha256 was not found in {metadata_path}")

    package_info = json.loads(package_info_path.read_text(encoding="utf-8-sig"))
    package_info["ApiHash"] = api_hash
    package_info_path.write_text(json.dumps(package_info, indent=2) + "\n", encoding="utf-8")
    print(f"Stored ApiHash in {package_info_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add API markdown hashes to PackageInfo files")
    parser.add_argument("--artifact-staging-directory", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    artifact_dir = pathlib.Path(args.artifact_staging_directory)
    repo_root = pathlib.Path(args.repo_root)
    package_info_dir = artifact_dir / "PackageInfo"
    export_script = repo_root / "eng" / "common" / "scripts" / "Export-APIViewMarkdown.ps1"

    for package_info_path in package_info_dir.glob("*.json"):
        package_info = json.loads(package_info_path.read_text(encoding="utf-8-sig"))
        package_name = package_info["Name"]
        package_artifact_dir = artifact_dir / package_name
        token_file = package_artifact_dir / f"{package_name}_python.json"
        # API stub generation intentionally omits management-plane packages, so they have no token file.
        # Revisit this behavior if management-plane packages are included in API stub generation.
        if not token_file.is_file():
            print(f"API token file was not found for {package_name}; skipping ApiHash update")
            continue

        subprocess.run(
            ["pwsh", str(export_script), "-TokenJsonPath", str(token_file), "-OutputPath", str(package_artifact_dir)],
            check=True,
        )
        extract_metadata(package_artifact_dir / "api.md")

        update_package_info(package_artifact_dir / "api.metadata.yml", package_info_path)


if __name__ == "__main__":
    main()