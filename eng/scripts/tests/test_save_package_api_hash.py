import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import save_package_api_hash


class SavePackageApiHashTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.artifact_dir = pathlib.Path(self.temp_dir.name)
        self.package_info_dir = self.artifact_dir / "PackageInfo"
        self.package_info_dir.mkdir()

    def write_package_info(self, name="azure-mgmt-test", **properties):
        path = self.package_info_dir / f"{name}.json"
        path.write_text(
            json.dumps({"Name": name, "Version": "1.0.0", "SdkType": "mgmt", **properties}),
            encoding="utf-8-sig",
        )
        return path

    def run_main(self):
        with patch.object(
            sys,
            "argv",
            [
                "save_package_api_hash.py",
                "--artifact-staging-directory",
                str(self.artifact_dir),
                "--repo-root",
                str(self.artifact_dir),
            ],
        ):
            save_package_api_hash.main()

    def test_missing_tokens_default_missing_or_blank_hashes(self):
        for properties in ({}, {"ApiHash": None}, {"ApiHash": ""}, {"ApiHash": "   "}):
            with self.subTest(properties=properties):
                path = self.write_package_info(**properties)
                with patch.object(save_package_api_hash.subprocess, "run") as export:
                    self.run_main()
                export.assert_not_called()
                self.assertEqual(
                    json.loads(path.read_text(encoding="utf-8")),
                    {"Name": "azure-mgmt-test", "Version": "1.0.0", "SdkType": "mgmt", "ApiHash": "dummy"},
                )

    def test_missing_tokens_preserve_existing_hash(self):
        path = self.write_package_info(ApiHash="existing-hash")
        self.run_main()
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["ApiHash"], "existing-hash")

    def test_generated_hash_and_dummy_in_same_run(self):
        management_path = self.write_package_info()
        generated_path = self.write_package_info("azure-test", ApiHash="dummy")
        package_dir = self.artifact_dir / "azure-test"
        package_dir.mkdir()
        token_file = package_dir / "azure-test_python.json"
        token_file.write_text("{}", encoding="utf-8")
        (package_dir / "api.md").write_text("```\nclass Test:\n```\n", encoding="utf-8")

        with patch.object(save_package_api_hash.subprocess, "run") as export:
            self.run_main()

        export.assert_called_once_with(
            [
                "pwsh",
                str(self.artifact_dir / "eng" / "common" / "scripts" / "Export-APIViewMarkdown.ps1"),
                "-TokenJsonPath",
                str(token_file),
                "-OutputPath",
                str(package_dir),
            ],
            check=True,
        )
        metadata = yaml.safe_load((package_dir / "api.metadata.yml").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(generated_path.read_text(encoding="utf-8"))["ApiHash"], metadata["apiHash"])
        self.assertEqual(len(metadata["apiHash"]), 64)
        self.assertEqual(json.loads(management_path.read_text(encoding="utf-8"))["ApiHash"], "dummy")

    def test_invalid_generated_metadata_still_fails(self):
        path = self.write_package_info()
        metadata_path = self.artifact_dir / "api.metadata.yml"
        original = path.read_bytes()
        for metadata in ({}, {"apiHash": None}, {"apiHash": ""}, {"apiHash": " "}, {"apiHash": 123}):
            with self.subTest(metadata=metadata):
                metadata_path.write_text(yaml.safe_dump(metadata), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "apiHash was not found"):
                    save_package_api_hash.update_package_info(metadata_path, path)
                self.assertEqual(path.read_bytes(), original)

    def test_export_failure_is_not_replaced_with_dummy(self):
        path = self.write_package_info("azure-test")
        package_dir = self.artifact_dir / "azure-test"
        package_dir.mkdir()
        (package_dir / "azure-test_python.json").write_text("{}", encoding="utf-8")
        with patch.object(
            save_package_api_hash.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "pwsh")
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                self.run_main()
        self.assertNotIn("ApiHash", json.loads(path.read_text(encoding="utf-8-sig")))


if __name__ == "__main__":
    unittest.main()
