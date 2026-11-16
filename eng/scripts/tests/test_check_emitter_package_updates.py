import contextlib
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import check_emitter_package_updates as checker


class CheckEmitterPackageUpdatesTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.package_file = pathlib.Path(self.directory.name) / "package.json"

    def write_manifest(self, dependencies):
        self.package_file.write_text(
            json.dumps({"dependencies": dependencies}), encoding="utf-8"
        )

    def test_no_watched_dependencies_fails(self):
        self.write_manifest({"unrelated": "1.0.0"})
        with self.assertRaisesRegex(ValueError, "No watched emitter dependencies"):
            checker.check_emitter_package_updates(self.package_file)

    def test_invalid_metadata_fails(self):
        self.write_manifest({"@typespec/compiler": "^1.0.0"})
        with patch.object(
            checker, "_run", return_value='{"versions": [], "dist-tags": {}}'
        ):
            with self.assertRaisesRegex(ValueError, "Invalid CFS metadata"):
                checker.check_emitter_package_updates(self.package_file)

    def test_missing_ncu_request_fails(self):
        self.write_manifest({"@typespec/compiler": "^1.0.0"})
        metadata = json.dumps({"versions": ["1.0.0"], "dist-tags": {"latest": "1.0.0"}})
        with patch.object(checker, "_run", side_effect=[metadata, "{}"]):
            with self.assertRaisesRegex(RuntimeError, "Could not resolve CFS versions"):
                checker.check_emitter_package_updates(self.package_file)

    def test_cli_emits_output_only_on_success(self):
        for upgrades, expected in (
            ({}, "false"),
            ({"@typespec/compiler": "^2.0.0"}, "true"),
        ):
            with self.subTest(upgrades=upgrades), patch.object(
                checker, "check_emitter_package_updates", return_value=upgrades
            ), patch.object(
                sys,
                "argv",
                ["check_emitter_package_updates.py", str(self.package_file)],
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    checker.main()
                self.assertIn(
                    f"##vso[task.setvariable variable=EmitterPackageHasUpdates;isOutput=true]{expected}",
                    output.getvalue(),
                )
        with patch.object(
            checker,
            "check_emitter_package_updates",
            side_effect=RuntimeError("feed error"),
        ), patch.object(
            sys, "argv", ["check_emitter_package_updates.py", str(self.package_file)]
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), self.assertRaisesRegex(
                RuntimeError, "feed error"
            ):
                checker.main()
            self.assertNotIn("##vso[task.setvariable", output.getvalue())


@unittest.skipUnless(
    shutil.which("npm") and shutil.which("ncu"),
    "npm and npm-check-updates are required",
)
class RegistryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                name = unquote(urlsplit(self.path).path).lstrip("/")
                if name in self.server.failures:
                    self.send_error(401, "Authentication required")
                    return
                metadata = self.server.packages.get(name)
                if metadata is None:
                    self.send_error(404)
                    return
                data = json.dumps(metadata).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, format, *args):
                pass

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.registry = f"http://127.0.0.1:{cls.server.server_port}/"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.package_file = pathlib.Path(self.directory.name) / "package.json"
        self.server.failures = set()
        self.server.packages = {}

    def add_package(self, name, versions, latest):
        self.server.packages[name] = {
            "name": name,
            "dist-tags": {"latest": latest},
            "versions": {
                version: {"name": name, "version": version} for version in versions
            },
        }

    def assert_matches_direct_ncu(self, dependencies):
        self.package_file.write_text(
            json.dumps({"dependencies": dependencies}), encoding="utf-8"
        )
        original = self.package_file.read_bytes()
        direct = subprocess.run(
            [
                shutil.which("ncu"),
                "--packageFile",
                str(self.package_file),
                "--registry",
                self.registry,
                "--filter",
                checker.FILTER,
                "--jsonUpgraded",
                "--loglevel",
                "error",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        expected = json.loads(direct.stdout)
        self.assertEqual(
            checker.check_emitter_package_updates(self.package_file, self.registry),
            expected,
        )
        self.assertEqual(self.package_file.read_bytes(), original)
        return expected

    def test_updates_unchanged_and_prerelease_match_ncu(self):
        versions = ["1.0.0", "1.2.0", "2.0.0-alpha.1"]
        self.add_package("@typespec/compiler", versions, "1.2.0")
        self.add_package("@azure-tools/typespec-python", ["0.4.0", "0.5.0"], "0.5.0")
        dependencies = {
            "@typespec/compiler": "^1.0.0",
            "@azure-tools/typespec-python": "0.4.0",
        }
        self.assertEqual(
            self.assert_matches_direct_ncu(dependencies),
            {"@typespec/compiler": "^1.2.0", "@azure-tools/typespec-python": "0.5.0"},
        )
        self.server.packages["@typespec/compiler"]["dist-tags"][
            "latest"
        ] = "2.0.0-alpha.1"
        self.assertEqual(
            self.assert_matches_direct_ncu({"@typespec/compiler": "^1.0.0"}),
            {"@typespec/compiler": "^1.2.0"},
        )
        self.assertEqual(
            self.assert_matches_direct_ncu({"@typespec/compiler": "^2.0.0-alpha.0"}),
            {"@typespec/compiler": "^2.0.0-alpha.1"},
        )
        self.server.packages["@typespec/compiler"]["dist-tags"]["latest"] = "1.0.0"
        self.assertEqual(
            self.assert_matches_direct_ncu({"@typespec/compiler": "^1.0.0"}), {}
        )

    def test_failed_feed_lookup_does_not_skip_silently(self):
        self.add_package("@typespec/compiler", ["1.0.0", "1.2.0"], "1.2.0")
        self.server.failures.add("@azure-tools/typespec-python")
        self.package_file.write_text(
            json.dumps(
                {
                    "dependencies": {
                        "@typespec/compiler": "^1.0.0",
                        "@azure-tools/typespec-python": "0.4.0",
                    }
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(RuntimeError, "npm failed"):
            checker.check_emitter_package_updates(self.package_file, self.registry)


if __name__ == "__main__":
    unittest.main()
