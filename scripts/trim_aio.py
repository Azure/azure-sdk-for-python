import logging
from pathlib import Path
import shutil
import sys


_LOGGER = logging.getLogger(__name__)


def trim(base_folder):
    base_folder = Path(base_folder)
    for aio_folder in Path(base_folder).glob("**/aio"):
        _LOGGER.info("Working on %s", aio_folder)
        shutil.rmtree(aio_folder)  # Let it throw at worst


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    trim(sys.argv[1])
