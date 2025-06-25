import os
import logging
import subprocess
import sys

def install_uv_devrequirements(pkg_path: str, allow_nonpresence: bool = False):
    """
    Installs the development requirements for a given package.

    Args:
        pkg_path (str): The path to the package directory.
    """

    dev_req_path = os.path.join(pkg_path, "dev_requirements.txt")

    if not os.path.exists(dev_req_path) and not allow_nonpresence:
        print(f"Development requirements file not found at {dev_req_path}")
        raise FileNotFoundError(f"Development requirements file not found at {dev_req_path}")

    try:
        command = [sys.executable, "-m", "uv", "pip", "install", "-r", dev_req_path]
        subprocess.run(command, check=True, cwd=pkg_path)
        logging.info(f"Successfully installed development requirements from {dev_req_path}.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install development requirements: {e}")
