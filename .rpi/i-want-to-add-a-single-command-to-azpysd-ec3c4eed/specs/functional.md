# Functional behavior — current azpysdk CLI and CI checks

Describes what exists today, relevant to adding a single `azpysdk ci`
aggregate command. No proposals.

## Invocation contract

- Usage: `azpysdk [global flags] <command> [target] [command flags]`.
- `<command>` is one of the registered check names (see architecture.md).
  There is currently **no** aggregate/"run everything" command such as `ci`
  or `all`; each check is invoked individually.
- `target` (positional, from the shared `common` parser) is a glob for
  packages. Default `"**"`; `.` means "the current directory as a single
  package". Example: `azpysdk pylint .` runs pylint on the package in cwd.
- Global/shared flags available to every check:
  - `--isolate` — run in an isolated uv/virtual environment (creates/reuses
    `.venv/<package>/.venv_<command>`).
  - `--pypi` — install from PyPI instead of the default CFS feed.
  - `--python VERSION` — python version for the isolated venv (requires
    `--isolate` + uv; otherwise `parser.error`).
  - `--service NAME` — scope discovery to `sdk/<NAME>` (`auto` treated as unset).
  - Logging: `--quiet` | `--verbose` | `--log-level {DEBUG,INFO,WARN,ERROR,FATAL}`.
- Exit behavior (`main()` in `azpysdk/main.py`):
  - No subcommand → prints help, returns `1`.
  - On success → prints `"<command> check completed with exit code <n>"` and
    returns `int(result or 0)`.
  - `KeyboardInterrupt` → returns `130`. Uncaught exception → logs error,
    returns `2`.
  - Env vars `PIP_INDEX_URL` / `UV_DEFAULT_INDEX` are saved and restored in a
    `finally` block; cwd is restored to the original.

## Per-check behavior (common shape)

Each check (e.g. `black`, `pylint`, `mypy`, `samples`) implements:
- `register()` — adds exactly one subparser named after the check and sets
  `func=self.run`. Checks may add their own extra flags (e.g. `samples`,
  `changelog` add nested subcommands).
- `run(args) -> int`:
  1. `set_envvar_defaults()` (some checks also set a proxy URL).
  2. `targeted = self.get_targeted_directories(args)` — resolve packages.
  3. For each package: `os.chdir(package)`, `get_executable(...)` to
     create/reuse the venv, `install_dev_reqs(...)`, install the pinned tool,
     run it, capture the exit code into a `results` list.
  4. Return `max(results)` (worst exit code), `0` if nothing ran.
- The check name (`args.command`) is used to derive: the venv directory suffix
  (`.venv_<command>`), the junit filename (`test-junit-<command>.xml` in
  `_build_pytest_args_base`), and the proxy URL key for proxy-backed checks.

### Enablement / opt-out semantics
- `is_check_enabled(package_path, check, default)` decides whether a check runs
  for a given package, based on that package's `pyproject.toml`
  (`tool`-style settings) and a `ci_enabled` flag.
- `CHECK_DEFAULTS = {"black": False}` — black is opt-in per package; every
  other check defaults ON.
- Some checks self-gate: e.g. `black.run` skips packages that opt out of black
  when running in CI (`in_ci()` truthy → `--check --diff` mode).
- `MUST_RUN_ENVS = ["bandit"]`.

## Which checks constitute "CI checks for my changes" today

There is no single command; the CI pipelines drive the set:

- Analyze stage (`eng/pipelines/templates/steps/analyze.yml`) runs these
  azpysdk checks via `dispatch_checks.py --checks=...`:
  `mypy`, `pyright`, `pylint`, `black`, `bandit`, `verifysdist`, `verifywhl`,
  `verify_keywords`, `apistub`, `breaking`, `update_snippet` (and `sphinx`
  exists as a check/step). Plus non-azpysdk common steps (changelog
  verification, path length, autorest, API review, etc.).
- Test/build stage (`eng/pipelines/templates/steps/build-test.yml`) runs the
  build set (`set_checks.py`): `whl, sdist, mindependency` for PRs
  (`PR_BUILD_SET`) or the `FULL_BUILD_SET`
  (`whl, sdist, import_all, latestdependency, mindependency, whl_no_aio`),
  plus `samples`.
- **Link verification is not part of azpysdk.** It is the common PowerShell
  step `eng/common/pipelines/templates/steps/verify-links.yml`
  (`Verify-Links.ps1`), unrelated to the Python check machinery. Any local
  "verify links" behavior would not currently be reachable through `azpysdk`.

## CI multi-check orchestration (existing precedent for running many checks)

- `eng/scripts/dispatch_checks.py` already runs multiple check names across
  multiple packages:
  - `-c/--checks` accepts a comma-separated list of check names.
  - Builds `combos = [(package, check)]` and runs them with bounded concurrency
    (`--max-parallel`, default CPU count) via `run_all_checks` /
    `run_check`.
  - Aggregates results into `CheckResult` records and reports
    `Total checks / Failed / Worst exit code`; returns the worst exit code.
  - Handles test-proxy startup when any check is in `INSTALL_AND_TEST_CHECKS`.
  - This is a Python script, not an `azpysdk` subcommand; it is invoked
    directly by pipeline YAML, not through `azpysdk`.

## Edge cases already handled

- Non-package target (`.` on a dir with no `setup.py`/`setup.cfg`) → logs an
  error and returns an empty target list (check yields `0`).
- `--service auto` and empty/`auto` service values are treated as "no service
  scope".
- Missing `dev_requirements.txt` → `install_dev_reqs` warns and skips.
- Non-isolated runs strip `eng/tools/azure-sdk-tools` from dev requirements
  (avoids reinstalling the tools package into the current env).
- Isolated CI runs prefer a prebuilt `azure-sdk-tools` wheel from
  `PREBUILT_WHEEL_DIR`/`.wheels`, falling back to editable install.
- Env var and cwd restoration guaranteed via `finally` in `main()`.
