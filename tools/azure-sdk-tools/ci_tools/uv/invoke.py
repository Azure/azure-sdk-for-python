import subprocess
import logging

from pytest import main as pytest_main

from ci_tools.functions import is_error_code_5_allowed

def uv_pytest(target_path: str, additional_args: list[str] = [], shell: bool = False) -> bool:
    logging.info(f"Invoke pytest for {target_path}")

    exit_code = 0

    if shell:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", target_path] + additional_args,
            check=False
        )
        exit_code = result.returncode
    else:
        exit_code = pytest_main(
            [target_path] + additional_args
        )

    if exit_code != 0:
        if exit_code == 5 and is_error_code_5_allowed():
            logging.info("Exit code 5 is allowed, continuing execution.")
            return True
        else:
            logging.info(f"pytest failed with exit code {exit_code}.")
            return False

    return True