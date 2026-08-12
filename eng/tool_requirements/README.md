# Static-analysis tool pins (`eng/tool_requirements/`)

Pinned versions of the third-party tools that the `azpysdk` checks install at
runtime (mypy, pylint, pyright, sphinx, black, bandit, breaking-change checker).

Historically these versions were hardcoded as constants inside each check module
(for example `MYPY_VERSION = "1.19.1"` in `azpysdk/mypy.py`). That made them
invisible to any tool that scans the repository's declared dependencies, so the
daily CFS warm-up (`eng/scripts/warm_cfs_feed.py`) could not pre-cache the tools
or — more importantly — their transitive dependencies. When an unpinned
transitive dependency released a new version, unauthenticated PR pipelines (which
can only read what CFS has already cached) failed.

These files are the single source of truth for those pins:

- The `azpysdk` checks load them via `azpysdk._tool_reqs`.
- The daily warm-up script scans them (alongside every `dev_requirements.txt` and
  `pyproject.toml`) and runs `pip download` so the full transitive closure is
  pulled through into the CFS feed.

Each file is an ordinary pip requirements file (one requirement per line, `#`
comments allowed). Files suffixed `_next` hold the "next"/vNext tool versions
tested by the `next-*` checks.

To bump a tool version, edit the relevant file here — do not add the version back
into the Python check modules.
