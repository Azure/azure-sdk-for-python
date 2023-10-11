import os, logging, glob, subprocess, sys


class ManagedVirtualEnv:
    def __init__(self, path: str, name: str):
        self.path = os.path.join(path, name)

    def create(self):
        logging.info("Creating virtual environment [{}]".format(self.path))
        subprocess.check_call([sys.executable, "-m", "venv", "ENV_DIR", self.path])
        self.python_executable = self._find_python_executable()
        self.lib_paths = self._find_lib_paths()

    def clear_venv(self):
        subprocess.check_call([sys.executable, "-m", "venv", "--clear", "ENV_DIR", self.path])

    def _find_python_executable(self):
        paths = glob.glob(os.path.join(self.path, "*", "python")) + glob.glob(
            os.path.join(self.path, "*", "python.exe")
        )
        if not paths:
            logging.error(f"Failed to find path to python executable in virtual env:{self.path}")
            sys.exit(1)
        return paths[0]
