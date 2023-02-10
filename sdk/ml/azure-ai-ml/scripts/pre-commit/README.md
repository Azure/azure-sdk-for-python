To enable pre-commit, you need to:
1) run `pip install -r ./dev_requirements.txt` under this folder to install the pre-commit hook
2) follow [tox guide](../../../../../doc/dev/dev_setup.md) to install tox and setup environment to run pylint locally
   1) `pip install tox tox-monorepo`
   2) `tox -c ../../../eng/tox/tox.ini -e pylint` under project root directory
3) run `pre-commit install -c ./scripts/pre-commit/pre-commit-config.yaml` to enable the pre-commit hook
