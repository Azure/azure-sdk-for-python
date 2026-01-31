# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import configargparse
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


ENV_LIVE_TEST = "AZURE_TEST_RUN_LIVE"
TEST_SETTING_FILENAME = "testsettings_local.cfg"

def PROXY_URL():
    # If PROXY_ASSETS_FOLDER is set, extract the port from the last folder
    proxy_assets_folder = os.getenv("PROXY_ASSETS_FOLDER")
    if proxy_assets_folder:
        # Remove trailing slashes and get the last path component
        folder = proxy_assets_folder.rstrip("/").rstrip("\\")
        port = os.path.basename(folder)
        # Verify it's a valid port number
        try:
            int(port)
            return f"http://localhost:{port}"
        except ValueError:
            pass  # Not a valid port, fall through to default

    return os.getenv("PROXY_URL", "http://localhost:5000").rstrip("/")

class TestConfig(object):  # pylint: disable=too-few-public-methods
    def __init__(self, parent_parsers=None, config_file=None):
        parent_parsers = parent_parsers or []
        self.parser = configargparse.ArgumentParser(parents=parent_parsers)
        self.parser.add_argument(
            "-c",
            "--config",
            is_config_file=True,
            default=config_file,
            help="Path to a configuration file in YAML format.",
        )
        self.parser.add_argument(
            "-l",
            "--live-mode",
            action="store_true",
            dest="live_mode",
            env_var=ENV_LIVE_TEST,
            help='Activate "live" recording mode for tests.',
        )
        self.args = self.parser.parse_args([])

    @property
    def record_mode(self):
        return self.args.live_mode
