# Poetry Proto

## Using poetry to verify requirements

Right now, I find it very hard to see how we could use poetry and also have some of intended test cases run, so I'm unclear on what that transition would look like. However, if we're looking just to use it for dependency resolution at the start, I can definitely see a path forward. The rest will fall out as smarter folks (read: laurent and sean) provide their input. [This little article](https://github.com/python-poetry/poetry/issues/366) also has some great tips.

So far, this is what I got:

1. Add a `pyproject.toml` and a `poetry.lock` to the root of our repository.
2. On PRs, detect updated `setup.py` files, deliberately reset the package lock for any packages that have an updated `setup.py`.
3. If a `conflict` is detected, block the PR.

This means that people will be able to get ahead of this by forcing the update of a package via a `poetry update` from the root of the repo. Or, if they hit an issue, they take action to resolve by `poetry update` follwed by updating their PR with the lock file update.

### How it works

The `pyproject.toml` is basically a skeleton to set up `path` dependencies on each and every package within our repo.

I generated this with a `poetry init` followed by manually adding paths that I grabbed using a simple globbing script.

### Provisos and gotchas

It handles unreleased packages fairly well, due to the fact that it takes each "local" requirement as a `==`. I'm super interested in gotchas from folks.

I discovered that we need to use their [extended dependency specification](https://python-poetry.org/docs/dependency-specification/#python-restricted-dependencies) for packages that are async only. This is due to the fact that we specify the required python as `^2.7 || >= 3.5.3`.

Frankly, I **love** the errors here.

```

(venv) PS C:\repo\sdk-for-python> poetry update
Updating dependencies
Resolving dependencies...

  SolverProblemError

  The current project's Python requirement (>=2.7,<3.0 || >=3.5.3) is not compatible with some of the required packages Python requirement:
    - azure-core-tracing-opentelemetry requires Python >=3.5.0, so it will not be satisfied for Python >=2.7,<3.0

  Because sdk-for-python depends on azure-core-tracing-opentelemetry (1.0.0b9) which requires Python >=3.5.0, version solving failed.

  at c:\repo\venv\lib\site-packages\poetry\puzzle\solver.py:241 in _solve
      237│             packages = result.packages
      238│         except OverrideNeeded as e:
      239│             return self.solve_in_compatibility_mode(e.overrides, use_latest=use_latest)
      240│         except SolveFailure as e:
    → 241│             raise SolverProblemError(e)
      242│
      243│         results = dict(
      244│             depth_first_search(
      245│                 PackageNode(self._package, packages), aggregate_package_nodes

  • Check your dependencies Python requirement: The Python requirement can be specified via the `python` or `markers` properties

    For azure-core-tracing-opentelemetry, a possible solution would be to set the `python` property to ">=3.5.3"

    https://python-poetry.org/docs/dependency-specification/#python-restricted-dependencies,
    https://python-poetry.org/docs/dependency-specification/#using-environment-markers
```

Was resolved by the following commit update:

```

-azure-core-tracing-opentelemetry = {path = "sdk/core/azure-core-tracing-opentelemetry"}
+azure-core-tracing-opentelemetry = {path = "sdk/core/azure-core-tracing-opentelemetry", python = ">=3.5.3"}
```

Poetry even _tells_ you that!

### Other discovered issues with these packages during initial setup

```
azure-schemaregistry-avroserializer = {path = "sdk/schemaregistry/azure-schemaregistry-avroserializer"}
azure-monitor-opentelemetry-exporter = {path = "sdk/monitor/azure-monitor-opentelemetry-exporter"}
```

Have issues because they have locked a dependency to a previous version from what's _present in the repo_. `poetry` obviously vomits all over itself here. There **aren't** resolvable paths for the current packages :)

### Long Term Support

Unfortunately, I have found that poetry [will be ending support](https://python-poetry.org/docs/#system-requirements) for py 2.7 and 3.5 in the 1.2 release. THis could be a concern going forward.
