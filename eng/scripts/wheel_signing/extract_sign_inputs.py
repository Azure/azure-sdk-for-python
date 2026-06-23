import argparse
import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List


SIGNABLE_SUFFIXES = {".so", ".dylib", ".dll", ".pyd"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract wheel files, collect signable binaries, and generate "
            "signing payloads plus a manifest for wheel repackaging."
        )
    )
    parser.add_argument("--platform", choices=["mac", "windows"], required=True)
    parser.add_argument("--wheels-dir", required=True, help="Directory containing input wheel files.")
    parser.add_argument("--work-dir", required=True, help="Working directory for unpacked wheels and manifest.")
    parser.add_argument(
        "--sign-input-zip",
        default=None,
        help="Output zip containing binaries to sign (required for --platform mac).",
    )
    parser.add_argument(
        "--sign-input-dir",
        default=None,
        help="Output folder containing binaries to sign (required for --platform windows).",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.platform == "mac":
        if not args.sign_input_zip:
            raise ValueError("--sign-input-zip is required for --platform mac.")
        if args.sign_input_dir:
            raise ValueError("--sign-input-dir is not valid for --platform mac.")
    else:
        if not args.sign_input_dir:
            raise ValueError("--sign-input-dir is required for --platform windows.")
        if args.sign_input_zip:
            raise ValueError("--sign-input-zip is not valid for --platform windows.")


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def collect_wheels(wheels_dir: Path) -> List[Path]:
    if not wheels_dir.is_dir():
        raise FileNotFoundError(f"Wheel directory not found: {wheels_dir}")
    return sorted(wheels_dir.rglob("*.whl"))


def collect_signable_files(unpacked_wheel_dir: Path) -> List[Path]:
    files = []
    for path in sorted(unpacked_wheel_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SIGNABLE_SUFFIXES:
            files.append(path)
    return files


def write_manifest(manifest_path: Path, manifest_data: Dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest_data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def create_zip_from_dir(source_dir: Path, output_zip: Path) -> None:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(source_dir).as_posix())


def main() -> None:
    args = parse_args()
    validate_args(args)

    wheels_dir = Path(args.wheels_dir).resolve()
    work_dir = Path(args.work_dir).resolve()
    unpack_root = work_dir / "unpacked"
    manifest_path = work_dir / "signing-manifest.json"

    if args.platform == "windows":
        payload_dir = Path(args.sign_input_dir).resolve()
    else:
        payload_dir = work_dir / "mac-sign-input"

    reset_dir(work_dir)
    reset_dir(unpack_root)
    reset_dir(payload_dir)

    wheels = collect_wheels(wheels_dir)
    print(f"Platform: {args.platform}")
    print(f"Input wheels dir: {wheels_dir}")
    print(f"Work dir: {work_dir}")

    manifest: Dict[str, object] = {
        "platform": args.platform,
        "wheels": [],
        "entries": [],
    }

    payload_index = 0

    for wheel_path in wheels:
        unpack_dir_name = wheel_path.name[:-4]
        unpacked_wheel_dir = unpack_root / unpack_dir_name
        unpacked_wheel_dir.mkdir(parents=True, exist_ok=True)
        print(f"[EXTRACT] wheel={wheel_path.name} unpack_dir={unpacked_wheel_dir}")

        with zipfile.ZipFile(wheel_path, "r") as archive:
            archive.extractall(unpacked_wheel_dir)

        manifest["wheels"].append(
            {
                "wheel_filename": wheel_path.name,
                "unpack_dir": unpack_dir_name,
            }
        )

        signable_files = collect_signable_files(unpacked_wheel_dir)
        print(f"[EXTRACT] wheel={wheel_path.name} signable_count={len(signable_files)}")
        for signable_file in signable_files:
            relative_path = signable_file.relative_to(unpacked_wheel_dir).as_posix()
            payload_name = f"{payload_index:05d}__{signable_file.name}"
            payload_index += 1

            payload_path = payload_dir / payload_name
            shutil.copy2(signable_file, payload_path)
            print(
                "[MAP_EXTRACT] "
                f"payload={payload_name} "
                f"source_wheel={wheel_path.name} "
                f"source_relative_path={relative_path} "
                f"source_file={signable_file} "
                f"payload_file={payload_path}"
            )

            manifest["entries"].append(
                {
                    "wheel_filename": wheel_path.name,
                    "unpack_dir": unpack_dir_name,
                    "relative_path": relative_path,
                    "payload_name": payload_name,
                }
            )

    write_manifest(manifest_path, manifest)

    if args.platform == "mac":
        sign_zip = Path(args.sign_input_zip).resolve()
        create_zip_from_dir(payload_dir, sign_zip)

    print(f"Wheels processed: {len(wheels)}")
    print(f"Signable binaries collected: {len(manifest['entries'])}")
    print(f"Manifest: {manifest_path}")
    if args.platform == "mac":
        print(f"Sign payload zip: {Path(args.sign_input_zip).resolve()}")
    else:
        print(f"Sign payload dir: {payload_dir}")


if __name__ == "__main__":
    main()
