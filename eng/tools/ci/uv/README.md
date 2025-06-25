# `uv` script checks for `azure-sdk-for-python`

The scripts contained within this directory are self-contained validation scripts that are intended to be used by CI and for local development.

## Example Check Invocations

- `uv run tools/ci/uv/<checkname>.py azure-core`
- `uv run tools/ci/uv/<checkname>.py azure-storage*`
- `uv run tools/ci/uv/<checkname>.py azure-storage-blob,azure-storage-queue`

## Outstanding questions

### Using tool instead of script?

- Should we instead create a root `pyproject.toml` for each of these and install as a `uv tool`?
  - ```
    tools/
      ci/
        uv/
          whl/
            whl.py
            pyproject.toml
    ```
  - Doing the above will allow us to install the check as a `tool` (which will have an isolated venv) and enable easy access via a named entrypoint on the PATH.
  - We will need to be more explicit about cleaning up the venv being used in CI, versus `uv run` which is purely ephemeral unless told otherwise.

###

## Guidelines for creating a uv check

- You **must** include `uv` in the list of dependencies for your script. This will enable access to `uv pip` from within the environment without assuming anything about a global `uv` install. This will enable `subprocess.run([sys.executable, '-m', 'uv', 'pip', 'install', 'packagename'])` with all the efficiency implied by using `uv`.
- You **must** `uv add --script tools/ci/uv/whl.py "-r eng/ci_tools.txt"` to ensure that the generic pinned dependencies are present on your script.
- You **must** cleave to the common argparse definition to ensure that all the checks have similar entrypoint behavior.
  - This does not exist yet.

## Transition from `tox` details

### Pros

- The speed is astonishing
- We get ephemeral venvs by default
- We can encode a ton more information due to the freedom of a pure-python script invoking all the work.

### Cons

- A single unified dependency file is not supported. When we update we will just have to `uv add --script <check.py> -r eng/ci_tools.txt` which will update all the PEP723 preambles for our check scripts.
- We will need to parallelize invocation of these environments ourselves and deal with any gotchas. We'll do that in `dispatch_uv.py` which will be a follow-up to `dispatch_tox.py`.