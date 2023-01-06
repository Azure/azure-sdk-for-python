# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This module simulate run() which can specify succeed every n items from argument."""
import argparse
from pathlib import Path


def init():
    """Init."""
    global OUTPUT_PATH

    parser = argparse.ArgumentParser(allow_abbrev=False, description="ParallelRunStep Agent")
    parser.add_argument("--job_output_path", type=str, default=0)
    args, _ = parser.parse_known_args()
    OUTPUT_PATH = args.job_output_path
    print("Pass through init done")


def run(mini_batch):
    """Run."""

    for file_path in mini_batch:
        file = Path(file_path)
        print("Processing {}".format(file))
        assert file.exists()

        # Two customers reported transient error when using OutputFileDatasetConfig.
        # It hits "FileNotFoundError" when writing to a file in the output_dir folder,
        #  even the folder did exist per logs.
        # This is to simulate such case and hope we can repro in our gated build.
        output_dir = Path(OUTPUT_PATH)
        print("output_dir", output_dir)
        print("output_dir exits", Path(output_dir).exists())
        (Path(output_dir) / file.name).write_text(file_path)

    return mini_batch
