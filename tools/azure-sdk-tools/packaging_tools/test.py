from subprocess import getoutput
import os
from pathlib import Path

os.chdir(str(Path("D:/dev/azure-sdk-for-python/sdk/consumption/azure-mgmt-consumption")))
output = getoutput("tox run -c ../../../eng/tox/tox.ini --root . -e breaking --  --changelog --latest-pypi-version")

x = os.linesep
result = [l for l in output.split(os.linesep)]
begin = result.index("===== changelog start =====")
end = result.index("===== changelog end =====")