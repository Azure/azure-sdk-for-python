# Round-trip coverage for extract_sign_inputs.py + repackage_signed_wheels.py.
#
# PR builds never run the Sign_* stages (ESRP is unreachable from public pipelines), so these
# scripts are otherwise only exercised end-to-end on scheduled/release runs. These tests fake
# out the ESRP step (mutate the extracted payload bytes in place) and assert the full
# extract -> "sign" -> repackage round trip: each binary lands back in the wheel/path it came
# from, unrelated files are untouched, and the rebuilt RECORD hashes/sizes are correct.

import csv
import hashlib
import base64
import sys
import zipfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import extract_sign_inputs  # noqa: E402
import repackage_signed_wheels  # noqa: E402


def _digest(content: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode("ascii").rstrip("=")


def _build_wheel(wheel_path: Path, dist_info_name: str, files: dict) -> None:
    """Builds a minimal wheel zip. `files` maps relative path -> bytes content.

    A `<dist_info_name>/RECORD` entry is always added (content is irrelevant; it is fully
    rewritten by repackage_signed_wheels).
    """
    wheel_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative_path, content in files.items():
            archive.writestr(relative_path, content)
        archive.writestr(f"{dist_info_name}/RECORD", "")


def _read_wheel(wheel_path: Path) -> dict:
    with zipfile.ZipFile(wheel_path, "r") as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def _assert_record_matches_contents(wheel_contents: dict, dist_info_name: str) -> None:
    record_name = f"{dist_info_name}/RECORD"
    rows = list(csv.reader(wheel_contents[record_name].decode("utf-8").splitlines()))
    rows_by_path = {row[0]: row for row in rows}

    # Every non-RECORD file present in the wheel must have a row with a matching hash/size.
    for name, content in wheel_contents.items():
        if name == record_name:
            continue
        assert name in rows_by_path, f"RECORD missing entry for {name}"
        _, digest_field, size_field = rows_by_path.pop(name)
        assert digest_field == f"sha256={_digest(content)}"
        assert size_field == str(len(content))

    # RECORD's own row must have empty hash/size, and no stale rows should remain.
    assert rows_by_path == {record_name: [record_name, "", ""]}


@pytest.mark.parametrize("suffix_case", ["lower", "upper"])
def test_windows_round_trip_multiple_wheels_and_duplicate_basenames(tmp_path, monkeypatch, suffix_case):
    wheels_dir = tmp_path / "wheels"

    pyd_ext = ".pyd" if suffix_case == "lower" else ".PYD"
    dll_ext = ".dll" if suffix_case == "lower" else ".DLL"

    # Two wheels intentionally reuse the same binary basenames to exercise the payload-index
    # based naming (00000/, 00001/, ...) that keeps same-named binaries from different wheels
    # from colliding in the shared signing payload directory.
    _build_wheel(
        wheels_dir / "pkg_one-1.0.0-cp310-abi3-win_amd64.whl",
        "pkg_one-1.0.0.dist-info",
        {
            f"pkg/native{pyd_ext}": b"unsigned-pyd-one",
            f"pkg/helper{dll_ext}": b"unsigned-dll-one",
            "pkg/__init__.py": b"# not signable",
        },
    )
    _build_wheel(
        wheels_dir / "pkg_two-2.0.0-cp310-abi3-win_amd64.whl",
        "pkg_two-2.0.0.dist-info",
        {
            f"pkg/native{pyd_ext}": b"unsigned-pyd-two",
            f"pkg/helper{dll_ext}": b"unsigned-dll-two",
            "pkg/__init__.py": b"# not signable",
        },
    )

    work_dir = tmp_path / "work"
    sign_input_dir = tmp_path / "sign-input"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "extract_sign_inputs.py",
            "--platform",
            "windows",
            "--wheels-dir",
            str(wheels_dir),
            "--work-dir",
            str(work_dir),
            "--sign-input-dir",
            str(sign_input_dir),
        ],
    )
    extract_sign_inputs.main()

    payload_files = sorted(p for p in sign_input_dir.rglob("*") if p.is_file())
    # Only .pyd/.dll were collected: 2 wheels x 2 signable files each, and the .py files were
    # left out of the signing payload entirely.
    assert len(payload_files) == 4
    assert {p.name.lower() for p in payload_files} == {f"native{pyd_ext}".lower(), f"helper{dll_ext}".lower()}

    # Duplicate basenames across wheels must not collide in the shared payload directory.
    assert len({p.parent.name for p in payload_files}) == 4

    # "Sign" every payload file in place, standing in for the ESRP step.
    for payload_file in payload_files:
        payload_file.write_bytes(payload_file.read_bytes() + b"-SIGNED")

    output_wheels_dir = tmp_path / "output-wheels"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "repackage_signed_wheels.py",
            "--platform",
            "windows",
            "--work-dir",
            str(work_dir),
            "--signed-input-dir",
            str(sign_input_dir),
            "--output-wheels-dir",
            str(output_wheels_dir),
        ],
    )
    repackage_signed_wheels.main()

    rebuilt_one = _read_wheel(output_wheels_dir / "pkg_one-1.0.0-cp310-abi3-win_amd64.whl")
    rebuilt_two = _read_wheel(output_wheels_dir / "pkg_two-2.0.0-cp310-abi3-win_amd64.whl")

    # Each signed binary returned to the wheel it was extracted from, not its sibling.
    assert rebuilt_one[f"pkg/native{pyd_ext}"] == b"unsigned-pyd-one-SIGNED"
    assert rebuilt_one[f"pkg/helper{dll_ext}"] == b"unsigned-dll-one-SIGNED"
    assert rebuilt_two[f"pkg/native{pyd_ext}"] == b"unsigned-pyd-two-SIGNED"
    assert rebuilt_two[f"pkg/helper{dll_ext}"] == b"unsigned-dll-two-SIGNED"

    # Non-signable files are untouched byte-for-byte.
    assert rebuilt_one["pkg/__init__.py"] == b"# not signable"
    assert rebuilt_two["pkg/__init__.py"] == b"# not signable"

    _assert_record_matches_contents(rebuilt_one, "pkg_one-1.0.0.dist-info")
    _assert_record_matches_contents(rebuilt_two, "pkg_two-2.0.0.dist-info")


def test_mac_round_trip_only_collects_mac_suffixes(tmp_path, monkeypatch):
    wheels_dir = tmp_path / "wheels"

    # A stray .pyd alongside real mac binaries checks that platform-specific suffix selection
    # (mac: .so/.dylib only) excludes Windows-only binary types even if one ends up in a mac
    # wheel by mistake.
    _build_wheel(
        wheels_dir / "pkg-1.0.0-cp310-abi3-macosx_11_0_arm64.whl",
        "pkg-1.0.0.dist-info",
        {
            "pkg/native.so": b"unsigned-so",
            "pkg/vendored.dylib": b"unsigned-dylib",
            "pkg/mistaken.pyd": b"should-not-be-signed",
            "pkg/__init__.py": b"# not signable",
        },
    )

    work_dir = tmp_path / "work"
    sign_input_zip = tmp_path / "mac-sign-input.zip"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "extract_sign_inputs.py",
            "--platform",
            "mac",
            "--wheels-dir",
            str(wheels_dir),
            "--work-dir",
            str(work_dir),
            "--sign-input-zip",
            str(sign_input_zip),
        ],
    )
    extract_sign_inputs.main()

    with zipfile.ZipFile(sign_input_zip, "r") as archive:
        payload_names = {Path(name).name for name in archive.namelist()}
    assert payload_names == {"native.so", "vendored.dylib"}

    # "Sign" the payload zip by rewriting its contents in place.
    extract_dir = tmp_path / "mac-payload-extracted"
    with zipfile.ZipFile(sign_input_zip, "r") as archive:
        archive.extractall(extract_dir)
    for payload_file in extract_dir.rglob("*"):
        if payload_file.is_file():
            payload_file.write_bytes(payload_file.read_bytes() + b"-SIGNED")
    signed_zip = tmp_path / "mac-signed.zip"
    with zipfile.ZipFile(signed_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for payload_file in sorted(extract_dir.rglob("*")):
            if payload_file.is_file():
                archive.write(payload_file, payload_file.relative_to(extract_dir).as_posix())

    output_wheels_dir = tmp_path / "output-wheels"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "repackage_signed_wheels.py",
            "--platform",
            "mac",
            "--work-dir",
            str(work_dir),
            "--signed-input-zip",
            str(signed_zip),
            "--output-wheels-dir",
            str(output_wheels_dir),
        ],
    )
    repackage_signed_wheels.main()

    rebuilt = _read_wheel(output_wheels_dir / "pkg-1.0.0-cp310-abi3-macosx_11_0_arm64.whl")

    assert rebuilt["pkg/native.so"] == b"unsigned-so-SIGNED"
    assert rebuilt["pkg/vendored.dylib"] == b"unsigned-dylib-SIGNED"
    # Never sent through the mac signing payload, so it must come back unchanged.
    assert rebuilt["pkg/mistaken.pyd"] == b"should-not-be-signed"
    assert rebuilt["pkg/__init__.py"] == b"# not signable"

    _assert_record_matches_contents(rebuilt, "pkg-1.0.0.dist-info")


def test_repackage_rejects_noop_signing(tmp_path, monkeypatch):
    """If the "signed" payload comes back byte-identical to the unsigned input (e.g. ESRP
    silently failed/no-op'd), repackage_signed_wheels must refuse to publish it rather than
    silently ship an unsigned binary as if it were signed."""
    wheels_dir = tmp_path / "wheels"
    _build_wheel(
        wheels_dir / "pkg-1.0.0-cp310-abi3-macosx_11_0_arm64.whl",
        "pkg-1.0.0.dist-info",
        {
            "pkg/native.so": b"unsigned-so",
            "pkg/__init__.py": b"# not signable",
        },
    )

    work_dir = tmp_path / "work"
    sign_input_zip = tmp_path / "mac-sign-input.zip"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "extract_sign_inputs.py",
            "--platform",
            "mac",
            "--wheels-dir",
            str(wheels_dir),
            "--work-dir",
            str(work_dir),
            "--sign-input-zip",
            str(sign_input_zip),
        ],
    )
    extract_sign_inputs.main()

    # Do NOT mutate the payload: this simulates ESRP returning the binary unchanged.
    output_wheels_dir = tmp_path / "output-wheels"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "repackage_signed_wheels.py",
            "--platform",
            "mac",
            "--work-dir",
            str(work_dir),
            "--signed-input-zip",
            str(sign_input_zip),
            "--output-wheels-dir",
            str(output_wheels_dir),
        ],
    )

    with pytest.raises(RuntimeError, match="byte-identical"):
        repackage_signed_wheels.main()
