# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Pytest for running all content understanding samples.

This test dynamically discovers sample files and runs them to ensure they execute without errors.
Only runs with live tests (no recording).
"""

import os
import sys
import subprocess
import pytest
from pathlib import Path
from devtools_testutils import is_live, is_live_and_not_recording


def get_sample_files():
    """Dynamically discover Python sample files in the samples directory."""
    # Get the samples directory path (relative to this test file)
    samples_dir = Path(__file__).parent.parent / "samples"
    
    # Get all .py files in the samples directory
    py_files = list(samples_dir.glob("*.py"))
    
    # Filter out non-sample files
    excluded_files = {
        "sample_helper.py",      # Helper module
        "env.sample",            # Environment sample file
    }
    
    # Return only sample files as Path objects
    return [f for f in py_files if f.name not in excluded_files]


@pytest.mark.live_test_only
@pytest.mark.parametrize("sample_file", get_sample_files())
def test_sample_execution(sample_file):
    if not is_live_and_not_recording():
      pytest.skip("This test requires live mode to run, as it involves large video files that are too big for test proxy to record")
      return

    """Test that a sample file can be executed without errors."""
    # Skip if sample file doesn't exist
    if not sample_file.exists():
        pytest.skip(f"Sample file {sample_file} does not exist")
    
    # Get the samples directory for working directory
    samples_dir = sample_file.parent
    
    try:
        # Run the sample file with Python
        # Use subprocess to capture any errors
        result = subprocess.run(
            [sys.executable, str(sample_file.name)],
            cwd=str(samples_dir),
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per sample
            env=os.environ.copy()  # Pass through environment variables
        )
        
        # Check if the sample executed successfully
        if result.returncode != 0:
            pytest.fail(
                f"Sample {sample_file.name} failed with return code {result.returncode}.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )
        
        # Sample executed successfully
        assert result.returncode == 0, f"Sample {sample_file.name} should execute successfully"
        
    except subprocess.TimeoutExpired:
        pytest.fail(f"Sample {sample_file.name} timed out after 5 minutes")
    except Exception as e:
        pytest.fail(f"Failed to execute sample {sample_file.name}: {str(e)}")


def test_all_samples_discovered():
    """Test that we can discover sample files."""
    sample_files = get_sample_files()
    assert len(sample_files) > 0, "Should discover at least one sample file"
    
    # Print discovered samples for debugging
    print(f"\nDiscovered {len(sample_files)} sample files:")
    for sample_file in sample_files:
        print(f"  - {sample_file.name}")
