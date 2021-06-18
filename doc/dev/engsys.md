# Engineering System Checks

Our PR validation and nightly live runs test a variety of checks and scenarios to ensure the Python libraries will run flawlessly across multiple Python versions and OSes. This guide will demonstrate how to run some of these checks locally, common troubleshooting tips for checks, and how to opt-in to some of the optional checks. Most of these steps occur during the "Analyze" step of a pipeline run.

* [EngSys Checks](#engsys-checks)
    * [pylint](#pylint)
* [Optional Checks](#optional-checks)
    * [mypy](#mypy)
    * [black](#black)
    * [autorest automation](#autorest-automation)

## EngSys Checks

### PyLint

[Pylint](https://pypi.org/project/pylint/) is a static code analysis tool which is automatically run on all PRs.

#### Running locally
It is best to run pylint using tox to reproduce the environment that is run in our pipelines:
```bash
tox -c ../../../eng/tox/tox.ini -e lint
```

### API StubGen

#### Running locally

### Verify whl

#### Running locally

### Verify whl

#### Running locally

### Breaking Changes

#### Running locally


## Optional Checks

### MyPy

[MyPy](https://pypi.org/project/mypy/) is a static analyzer for type checking.

#### Opt-in
To opt-in, add the package name to the end of the [`mypy_hard_failure_packages.py`](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/tox/mypy_hard_failure_packages.py) file:

```python
MYPY_HARD_FAILURE_OPTED = [
    ...,
    "azure-my-package",
]
```

#### Running locally
MyPy can be run using tox.

```bash
tox -c ../../../eng/tox/tox.ini -e mypy
```

### black

[black](https://pypi.org/project/black) is an opinionated code formatter for Python source code.

#### Opt-in

Make the following change to your projects `ci.yml`:

```yml
extends:
    template: ../../eng/pipelines/templates/stages/archetype-sdk-client.yml
    parameters:
        ...
        ValidateFormatting: true
        ...
```

#### Running locally
To run locally first install `black` from pip if you do not have it already (the pipeline uses version 21.6b0). Currently, we use the `-l 120` option to allow lines up to 120 characters (consistent with our `pylint` check).
```bash
python -m pip install black==21.6b0
python -m black -l 120 <path/to/service_directory>
```

### Autorest Automation
This check will automatically create PRs with updated generated code whenever autorest has made an update that results in a change to the generated code for a package. Note: this check only runs in nightly CI checks.

#### Opt-in

Make the following change to your projects `ci.yml`:

```yml
extends:
    template: ../../eng/pipelines/templates/stages/archetype-sdk-client.yml
    parameters:
        ...
        VerifyAutorest: true
        ...
```

#### Running locally

To run autorest automation locally run the following command from the home of `azure-sdk-for-python`
```bash
azure-sdk-for-python> python scripts/devop_tasks/verify_autorest.py --service_directory <your_service_directory>
```