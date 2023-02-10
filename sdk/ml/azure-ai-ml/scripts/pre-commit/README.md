To enable pre-commit, you need to:
1) run `pip install -r ./dev_requirements.txt` under this folder to install the pre-commit hook
2) Copy [./pre-commit-config.yaml](./pre-commit-config.yaml) to the repo root directory and rename it to
".pre-commit-config.yaml"
3) follow [tox guide](../../../../../doc/dev/dev_setup.md) to install tox and setup environment to run pylint locally
   1) `pip install tox tox-monorepo`
   2) `tox -c ../../../eng/tox/tox.ini -e pylint` under project root directory
4) run `pre-commit install` to enable the pre-commit hook
