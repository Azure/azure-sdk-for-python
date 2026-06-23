import argparse
import base64
import csv
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reinsert signed binaries into unpacked wheel trees and rebuild wheel files "
            "with original filenames."
        )
    )
    parser.add_argument("--platform", choices=["mac", "windows"], required=True)
    parser.add_argument("--work-dir", required=True, help="Working directory created by extract_sign_inputs.py.")
    parser.add_argument(
        "--signed-input-zip",
        default=None,
        help="Signed binary zip payload (required for --platform mac).",
    )
    parser.add_argument(
        "--signed-input-dir",
        default=None,
        help="Signed binary folder payload (required for --platform windows).",
    )
    parser.add_argument("--output-wheels-dir", required=True, help="Directory where rebuilt wheel files are written.")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.platform == "mac":
        if not args.signed_input_zip:
            raise ValueError("--signed-input-zip is required for --platform mac.")
        if args.signed_input_dir:
            raise ValueError("--signed-input-dir is not valid for --platform mac.")
    else:
        if not args.signed_input_dir:
            raise ValueError("--signed-input-dir is required for --platform windows.")
        if args.signed_input_zip:
            raise ValueError("--signed-input-zip is not valid for --platform windows.")


def load_manifest(manifest_path: Path) -> Dict:
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def get_digest_and_size(file_path: Path) -> List[str]:
    content = file_path.read_bytes()
    digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode("ascii").rstrip("=")
    return [f"sha256={digest}", str(len(content))]


def find_record_path(unpacked_wheel_dir: Path) -> Path:
    candidates = sorted(unpacked_wheel_dir.glob("*.dist-info/RECORD"))
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one RECORD file under {unpacked_wheel_dir}, found {len(candidates)}."
        )
    return candidates[0]


def rewrite_record(unpacked_wheel_dir: Path) -> None:
    record_path = find_record_path(unpacked_wheel_dir)
    record_rel = record_path.relative_to(unpacked_wheel_dir).as_posix()

    rows: List[List[str]] = []
    for file_path in sorted(unpacked_wheel_dir.rglob("*")):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(unpacked_wheel_dir).as_posix()
        if rel == record_rel:
            continue
        digest, size = get_digest_and_size(file_path)
        rows.append([rel, digest, size])

    rows.append([record_rel, "", ""])

    with record_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(rows)


def build_wheel(unpacked_wheel_dir: Path, output_wheel_path: Path) -> None:
    output_wheel_path.parent.mkdir(parents=True, exist_ok=True)
    if output_wheel_path.exists():
        output_wheel_path.unlink()

    rewrite_record(unpacked_wheel_dir)

    with zipfile.ZipFile(output_wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(unpacked_wheel_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(unpacked_wheel_dir).as_posix())


def main() -> None:
    args = parse_args()
    validate_args(args)

    work_dir = Path(args.work_dir).resolve()
    unpack_root = work_dir / "unpacked"
    manifest_path = work_dir / "signing-manifest.json"
    output_wheels_dir = Path(args.output_wheels_dir).resolve()

    manifest = load_manifest(manifest_path)
    if manifest.get("platform") != args.platform:
        raise RuntimeError(
            f"Manifest platform '{manifest.get('platform')}' does not match argument platform '{args.platform}'."
        )

    if not unpack_root.is_dir():
        raise FileNotFoundError(f"Unpacked wheel directory not found: {unpack_root}")

    print(f"Platform: {args.platform}")
    print(f"Work dir: {work_dir}")
    print(f"Manifest: {manifest_path}")

    with tempfile.TemporaryDirectory(prefix="signed-binaries-") as tmpdir:
        if args.platform == "mac":
            signed_payload_dir = Path(tmpdir) / "signed-payload"
            signed_payload_dir.mkdir(parents=True, exist_ok=True)
            signed_zip = Path(args.signed_input_zip).resolve()
            if not signed_zip.is_file():
                raise FileNotFoundError(f"Signed payload zip not found: {signed_zip}")
            with zipfile.ZipFile(signed_zip, "r") as archive:
                archive.extractall(signed_payload_dir)
            print(f"Signed payload zip: {signed_zip}")
        else:
            signed_payload_dir = Path(args.signed_input_dir).resolve()
            if not signed_payload_dir.is_dir():
                raise FileNotFoundError(f"Signed payload directory not found: {signed_payload_dir}")
            print(f"Signed payload dir: {signed_payload_dir}")

        for entry in manifest.get("entries", []):
            wheel_filename = entry["wheel_filename"]
            unpack_dir = entry["unpack_dir"]
            relative_path = entry["relative_path"]
            payload_name = entry["payload_name"]

            source_signed_binary = signed_payload_dir / payload_name
            target_binary = unpack_root / unpack_dir / relative_path

            if not source_signed_binary.is_file():
                raise FileNotFoundError(f"Signed binary missing: {source_signed_binary}")
            if not target_binary.is_file():
                raise FileNotFoundError(f"Target binary missing in unpacked wheel: {target_binary}")

            shutil.copy2(source_signed_binary, target_binary)
            print(
                "[MAP_REPACKAGE] "
                f"payload={payload_name} "
                f"target_wheel={wheel_filename} "
                f"target_relative_path={relative_path} "
                f"signed_source={source_signed_binary} "
                f"target_file={target_binary}"
            )

    reset_dir(output_wheels_dir)

    rebuilt_count = 0
    for wheel_info in manifest.get("wheels", []):
        wheel_filename = wheel_info["wheel_filename"]
        unpack_dir = wheel_info["unpack_dir"]

        unpacked_wheel_dir = unpack_root / unpack_dir
        if not unpacked_wheel_dir.is_dir():
            raise FileNotFoundError(f"Unpacked wheel directory missing: {unpacked_wheel_dir}")

        output_wheel_path = output_wheels_dir / wheel_filename
        print(
            "[REBUILD] "
            f"wheel={wheel_filename} "
            f"unpacked_dir={unpacked_wheel_dir} "
            f"output_wheel={output_wheel_path}"
        )
        build_wheel(unpacked_wheel_dir, output_wheel_path)
        rebuilt_count += 1

    print(f"Wheels rebuilt: {rebuilt_count}")
    print(f"Output wheels dir: {output_wheels_dir}")


if __name__ == "__main__":
    main()
