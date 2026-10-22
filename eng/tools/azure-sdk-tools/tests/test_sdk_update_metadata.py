import os
import tempfile
import shutil
import json
from pathlib import Path

from packaging_tools.sdk_update_metadata import main as update_metadata_main


def test_metadata_update_invoked_with_tsp_and_emitter(monkeypatch):
    temp_dir = tempfile.mkdtemp()
    original_cwd = Path.cwd()
    try:
        pkg = Path(temp_dir) / "azure-mgmt-test"
        pkg.mkdir(parents=True)

        # tsp-location.yaml with required fields
        (pkg / "tsp-location.yaml").write_text(
            """commit: deadbeef1234567890\nrepo: https://github.com/Azure/azure-rest-api-specs\ndirectory: specification/test/resource-manager/readme.md\n"""
        )

        # emitter-package.json in expected relative location
        eng_dir = Path(temp_dir) / "eng"
        eng_dir.mkdir()
        (eng_dir / "emitter-package.json").write_text(
            json.dumps({"dependencies": {"@azure-tools/typespec-python": "1.2.3"}})
        )

        captured = {}

        def fake_update_metadata_json(package_path, *, pipeline_input, codegen_config, spec_folder, input_readme):  # type: ignore[override]
            captured["package_path"] = package_path
            captured["pipeline_input"] = pipeline_input
            captured["codegen_config"] = codegen_config
            captured["spec_folder"] = spec_folder
            captured["input_readme"] = input_readme

        def fake_generate_packaging_and_ci_files(package_path):  # type: ignore[override]
            captured["generate_called"] = True

        def fake_check_file(package_path):  # type: ignore[override]
            captured["check_file_called"] = True

        import packaging_tools.sdk_update_metadata as mod

        monkeypatch.setattr(mod, "update_metadata_json", fake_update_metadata_json)
        monkeypatch.setattr(mod, "generate_packaging_and_ci_files", fake_generate_packaging_and_ci_files)
        monkeypatch.setattr(mod, "check_file", fake_check_file)

        # Ensure relative lookup for eng/emitter-package.json succeeds
        monkeypatch.chdir(temp_dir)

        # Run
        update_metadata_main(pkg)

        # Assertions
        assert captured["package_path"] == pkg
        assert captured["pipeline_input"]["headSha"] == "deadbeef1234567890"
        assert captured["pipeline_input"]["repoHttpsUrl"] == "https://github.com/Azure/azure-rest-api-specs"
        assert captured["codegen_config"]["emitterVersion"] == "1.2.3"
        assert "specification/test/resource-manager/readme.md" in captured["input_readme"]
        assert captured.get("generate_called") is True
        # name contains azure-mgmt- so check_file should be called
        assert captured.get("check_file_called") is True
    finally:
        # Ensure we are not inside the directory we want to delete (Windows lock)
        try:
            os.chdir(original_cwd)
        except Exception:
            pass
        shutil.rmtree(temp_dir)


def test_metadata_update_skipped_without_info(monkeypatch):
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir) / "testpkg"
        pkg.mkdir(parents=True)

        import packaging_tools.sdk_update_metadata as mod

        called = {"update": False}

        def fake_update_metadata_json(*args, **kwargs):  # type: ignore[override]
            called["update"] = True

        def fake_generate_packaging_and_ci_files(package_path):  # type: ignore[override]
            called["generate"] = True

        monkeypatch.setattr(mod, "update_metadata_json", fake_update_metadata_json)
        monkeypatch.setattr(mod, "generate_packaging_and_ci_files", fake_generate_packaging_and_ci_files)

        update_metadata_main(pkg)

        # No tsp-location.yaml or emitter-package.json ==> update should not occur
        assert called["update"] is False
        # generate_packaging_and_ci_files always attempted
        assert called.get("generate") is True
    finally:
        shutil.rmtree(temp_dir)
