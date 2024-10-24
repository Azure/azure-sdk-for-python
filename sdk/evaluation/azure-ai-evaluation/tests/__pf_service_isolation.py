"""Ensure isolation of the .promptflow directory if test suite is invoked through tox.

.. note::

    This is especially relevant when run in the ci for Azure/azure-sdk-for-python, since 3 instances of the test suite
    are run in parallel (using `tox run-parallel`).

    Giving each process its own promptflow directory should allow each pytest session to better manage the life cycle
    of its promptflow service (and avoid issues when the service gets orphaned even after attempts to clean it up).

.. warning::

    This module has side-effects!

    Importing this module will relocate the promptflow home directory if the test suite is run through tox.

"""

import os
from pathlib import Path

if "TOX_ENV_DIR" in os.environ:
    os.environ["PF_HOME_DIRECTORY"] = str(Path(os.environ["TOX_ENV_DIR"], ".promptflow"))

    import promptflow._sdk._constants

    # Reduce the potential for parallel tox invocations to try to spawn their PF SERVICE on identical ports
    promptflow._sdk._constants.PF_SERVICE_DEFAULT_PORT += hash(os.environ["TOX_ENV_DIR"]) % 300
