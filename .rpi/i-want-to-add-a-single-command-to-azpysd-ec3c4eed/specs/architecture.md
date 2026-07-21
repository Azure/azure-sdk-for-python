# Architecture — azpysdk CLI and CI check dispatch

Scope: the `azpysdk` command-line tool, how individual checks are defined and
registered, and how CI selects/dispatches the set of checks that run for a
package. This is the machinery a new `azpysdk ci` command would build on.

## Entry point and command registration

- `eng/tools/azure-sdk-tools/azpysdk/main.py`
  - `build_parser()` — creates the top-level `argparse.ArgumentParser` (prog
    `azpysdk`). Defines global flags `--isolate`, `--pypi`, `--python`, and the
    logging group (`--quiet`/`--verbose`/`--log-level`).
  - Defines a shared `common` parser (`add_help=False`) that carries the
    `target` positional (glob, default `"**"`), plus `--isolate`, `--pypi`,
    `--python`, and `--service`. This `common` parser is passed as a parent to
    every subcommand so all checks share the same base options.
  - `subparsers = parser.add_subparsers(title="commands", dest="command")` — the
    chosen subcommand name is stored in `args.command`.
  - Every check is registered via `<check>().register(subparsers, [common])`.
    Currently registered command names (in order):
    `import_all, mypy, next_mypy, pylint, next_pylint, sphinx, next_sphinx,
    black, pyright, next_pyright, verifytypes, apistub, verify_sdist, whl,
    sdist, whl_no_aio, verify_whl, bandit, verify_keywords, generate, breaking,
    mindependency, latestdependency, samples, devtest, optional, update_snippet,
    changelog`.
  - `main(argv)` — parses args, calls `configure_logging`, sets pip/uv index
    env defaults (CFS feed unless `--pypi`), validates `--python`/`--isolate`,
    then dispatches via `result = args.func(args)` and prints
    `f"{args.command} check completed with exit code {result}"`. Returns the
    int exit code. If no `func` is set it prints help and returns 1.

- Console-script / module invocation: `python -m azpysdk.main` or the installed
  `azpysdk` entry (resolved to `venv/bin/azpysdk` in this workspace). Packaged
  under `eng/tools/azure-sdk-tools/azpysdk/`.

## Base check class

- `eng/tools/azure-sdk-tools/azpysdk/Check.py` — `class Check(abc.ABC)`:
  - `register(subparsers, parent_parsers)` — **abstract**; each check adds its
    own `subparsers.add_parser(<name>, parents=parents)` and calls
    `p.set_defaults(func=self.run)`.
  - `run(args) -> int` — default returns 0; each check overrides it.
  - `create_venv(isolate, venv_location, python_version)` — creates/reuses an
    isolated uv/venv; installs `azure-sdk-tools` (prebuilt wheel in CI, else
    editable) when isolating; returns the python executable (or `sys.executable`
    when not isolating).
  - `get_executable(isolate, check_name, executable, package_folder, python_version)`
    — computes a per-package shared venv dir under
    `REPO_ROOT/.venv/<package>/.venv_<check_name>` (the venv dir is keyed on
    `check_name`, which is `args.command`), returns `(executable, staging_dir)`.
  - `run_venv_command(...)` — runs a command inside the venv (adjusts PATH /
    VIRTUAL_ENV).
  - `get_targeted_directories(args) -> List[ParsedSetup]` — resolves which
    packages to run against. `target == "."` → current dir; otherwise uses
    `discover_targeted_packages(args.target, targeted_dir)`, honoring
    `--service` (a value of `"auto"` is treated as unset).
  - `install_dev_reqs(...)`, `pip_freeze(...)`, `_build_pytest_args*(...)`,
    `get_check_version(...)` — shared helpers.
  - Module constants: `REPO_ROOT = discover_repo_root()`,
    `TEST_TOOLS_REQUIREMENTS`, `DEPENDENCY_TOOLS_REQUIREMENTS`,
    `PACKAGING_REQUIREMENTS`.

## Representative check implementations

- `eng/tools/azure-sdk-tools/azpysdk/black.py` — `class black(Check)`:
  `register` adds parser `"black"`; `run` iterates `get_targeted_directories`,
  `get_executable`, `install_dev_reqs`, then installs pinned black and runs it.
  In CI (`in_ci()`) it runs `--check --diff` and honors
  `is_check_enabled(package_dir, "black", default=False)`. Returns
  `max(results)`.
- `eng/tools/azure-sdk-tools/azpysdk/samples.py` — `class samples(Check)`:
  same register/run shape; uses `args.command` to derive proxy URL and junit
  paths.
- `eng/tools/azure-sdk-tools/azpysdk/changelog.py` — example of a check that
  registers **nested subcommands** (`add`/`verify`/`create`/`status`) under its
  own parser.
- All checks follow the pattern: `register()` adds one parser and sets
  `func=self.run`; `run(args)` loops packages and returns the worst exit code.
  Each `run()` reads `args.command` for venv naming, junit filenames, and proxy
  URL selection.

## CI dispatch (how "the checks that run for my changes" are selected today)

- `eng/scripts/dispatch_checks.py` — the single CI entry that runs one or many
  checks across in-scope packages.
  - `main()` (argparse): positional `glob_string`; options `--service`,
    `-c/--checks` (`dest="checks_list"`, comma-separated names), `--junitxml`,
    `--mark_arg`, `--filter-type`, `--max-parallel`, `-w/--wheel_dir`,
    `-i/--injected-packages`, `-d/--dest-dir`,
    `--disable-compatibility-filter`, `--disablecov`.
  - Phase 1: discover in-scope packages (`discover_targeted_packages`).
  - Phase 2: `run_all_checks(packages, checks, max_parallel, ...)` builds
    `combos = [(p, c) for p in packages for c in checks]` and runs each via
    `run_check(...)`, gated by
    `is_check_enabled(package, check, CHECK_DEFAULTS.get(check, True))`.
  - `INSTALL_AND_TEST_CHECKS = {whl, whl_no_aio, sdist, devtest, optional,
    import_all, latestdependency, mindependency}` — these require test-proxy
    recording restore; `_checks_require_recording_restore(checks)` triggers
    proxy startup in CI.
  - `get_check_dest_dir(...)` — apistub output goes to a per-package subdir.

- `eng/scripts/set_checks.py` — computes the build-check set for a run:
  - `FULL_BUILD_SET = [whl, sdist, import_all, latestdependency, mindependency,
    whl_no_aio]`
  - `PR_BUILD_SET = [whl, sdist, mindependency]`
  - `process_ci_skips(...)` lists globally-skippable checks:
    `pylint, verifywhl, verifysdist, bandit, mypy, pyright, verifytypes`.
  - Sets the DevOps `checks` variable via `set_ci_variable`.

- Check-enablement rules: `eng/tools/azure-sdk-tools/ci_tools/environment_exclusions.py`
  - `CHECK_DEFAULTS = {"black": False}` (all other checks default ON).
  - `MUST_RUN_ENVS = ["bandit"]`.
  - `is_check_enabled(package_path, check, default)` reads each package's
    `pyproject.toml` (`get_config_setting`) and `ci_enabled` flag to decide
    per-package opt-in/opt-out.

## CI pipeline templates (which azpysdk checks CI actually invokes)

- `eng/pipelines/templates/steps/analyze.yml` — the analyze stage. Invokes
  `dispatch_checks.py` with `--checks=` for: `verifysdist`, `verifywhl`,
  `verify_keywords`, and includes step templates that call dispatch with:
  `mypy` (`run_mypy.yml`), `pyright` (`run_pyright.yml`), `pylint`
  (`run_pylint.yml`), `black` (`run_black.yml`), `bandit` (`run_bandit.yml`),
  `apistub` (`run_apistub.yml`), `breaking` (`run_breaking_changes.yml`),
  `update_snippet` (`update_snippet.yml`). Also runs non-azpysdk common
  steps: `verify-changelog(s).yml`, `verify-path-length.yml`,
  `verify-autorest.yml`, `create-apireview.yml`, `detect-api-changes.yml`,
  `validate-all-packages.yml`.
- `eng/pipelines/templates/steps/build-test.yml` — the test stage. Runs
  `dispatch_checks.py` with `--checks="${{ parameters.CheckEnv }}"` (the build
  set from `set_checks.py`) and `--checks="samples"`.
- **Link verification is NOT an azpysdk check.** It is a separate common
  PowerShell step: `eng/common/pipelines/templates/steps/verify-links.yml`
  invoking `Verify-Links.ps1`. Referenced in `eng/pipelines/aggregate-reports.yml`.

## Data flow summary

1. User runs `azpysdk <command> [target]` → `build_parser()` → `main()` →
   `args.func(args)` for the single named check.
2. A check's `run()` → `get_targeted_directories()` → per package:
   `get_executable()` (venv), `install_dev_reqs()`, run tool, collect exit code.
3. In CI, `dispatch_checks.py` is the multi-check orchestrator; the *set* of
   check names is decided by pipeline YAML (`analyze.yml`/`build-test.yml`) and
   `set_checks.py`, then filtered per package by `is_check_enabled`.
