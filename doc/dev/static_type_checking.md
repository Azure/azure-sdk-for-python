# Python SDK Static Type Checking Guide

This document contains some general typing tips and guidance as it relates to common types/patterns we use in the Python SDK.
It also walks through the setup necessary to run mypy and pyright, static type checkers, on client library code.

For the TL;DR version, please see the [Static Type Checking Cheat Sheet](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md).

## Table of contents
  - [Intro to typing in Python](#intro-to-typing-in-python)
  - [Typing a client library](#typing-a-client-library)
  - [Types usable in annotations](#types-usable-in-annotations)
  - [Install and run type checkers on your client library code](#install-and-run-type-checkers-on-your-client-library-code)
    - [Run mypy](#run-mypy)
    - [Run pyright](#run-pyright)
    - [Run verifytypes](#run-verifytypes)
    - [How to ignore type checking errors](#how-to-ignore-type-checking-errors)
    - [How to opt out of type checking](#how-to-opt-out-of-type-checking)
  - [Typing tips and guidance for the Python SDK](#typing-tips-and-guidance-for-the-python-sdk)
    - [Use typing.Any sparingly](#use-typingany-sparingly)
    - [Use typing.Union when accepting more than one type](#use-typingunion-when-accepting-more-than-one-type)
    - [Use typing.Optional when a parameter can explicitly be None](#use-typingoptional-when-a-parameter-can-explicitly-be-none)
    - [Typing for collections](#typing-for-collections)
      - [Mapping types](#mapping-types)
      - [List](#list)
      - [Tuples](#tuples)
    - [Parameters not needing type annotations](#parameters-not-needing-type-annotations)
    - [Typing variadic arguments - *args and **kwargs](#typing-variadic-arguments---args-and-kwargs)
    - [Use TYPE_CHECKING to avoid circular imports](#use-type_checking-to-avoid-circular-imports)
    - [Passing a function or a class as a parameter or return type](#passing-a-function-or-a-class-as-a-parameter-or-return-type)
    - [Use forward references when a type does not exist yet](#use-forward-references-when-a-type-does-not-exist-yet)
    - [Use type aliases to create readable names for types](#use-type-aliases-to-create-readable-names-for-types)
    - [Use typing.overload to overload a function](#use-typingoverload-to-overload-a-function)
    - [Use typing.cast to help the type checker understand a type](#use-typingcast-to-help-the-type-checker-understand-a-type)
    - [Use typing.TypeVar and typing.Generic for generic type hinting](#use-typingtypevar-and-typinggeneric-for-generic-type-hinting)
    - [Use AnyStr when your parameter or return type expects both str and bytes](#use-anystr-when-your-parameter-or-return-type-expects-both-str-and-bytes)
    - [Use typing.Protocol to support duck typing](#use-typingprotocol-to-support-duck-typing)
      - [Use runtime_checkable to do simple, runtime structural checks on Protocols](#use-runtime_checkable-to-do-simple-runtime-structural-checks-on-protocols)
    - [Use typing.Literal to restrict based on exact values](#use-typingliteral-to-restrict-based-on-exact-values)
    - [Use typing.NewType to restrict a type to a specific context](#use-typingnewtype-to-restrict-a-type-to-a-specific-context)
    - [Use typing.Final and @final to restrict types from changes](#use-typingfinal-and-final-to-restrict-types-from-changes)
    - [Debug type checking with reveal_type and reveal_locals](#debug-type-checking-with-reveal_type-and-reveal_locals)
  - [Additional Resources](#additional-resources)

## Intro to typing in Python

Python is a dynamically typed (or sometimes
called "[duck typed](https://docs.python.org/3/glossary.html#term-duck-typing)") language. This means that the
interpreter only checks types as code runs and types are allowed to change. This is different from more statically typed
languages, like Java, where you will have to declare types in code and check them at compile time. However,
with [PEP 483](https://peps.python.org/pep-0483/)/[PEP 484](https://peps.python.org/pep-0484/), type hints were
introduced to Python which makes it possible to do static type checking of Python code. Type hints can be written into
Python code to indicate the type of a variable, argument, return type, etc. There are tools available to perform static
type checking of type hints, like [mypy](https://mypy.readthedocs.io/en/stable/) and [pyright](https://github.com/microsoft/pyright).
Note that type hints do not affect the code at runtime and are not enforced by the interpreter.

There are some key benefits to using and checking type hints in Python code:

1) Type hints checked by a static type checker can help developers find bugs in Python code (type hints can be thought
   of as "free" unit tests, although they do not replace a thorough test suite).
2) Type hints are shipped in our packages so that customers can use them to further type check their own
   applications and get improved IDE and Intellisense experiences.
3) Type hints act as documentation in code and inform the reader of the expected types. This benefits us - the developers of the Python SDK!

Since Python 3, type annotations were introduced and are the **preferred** method of adding type hints to your code.
Annotations provide a cleaner syntax and let you keep the type information closer, or inline with the code.

```python
from typing import Any, Union

def download_blob_from_url(
        blob_url: str,
        output: str,
        credential: Union[AzureNamedKeyCredential, TokenCredential],
        overwrite: bool = False,
        **kwargs: Any
) -> None:
    ...
```

> Note: Do not use comment style type hints (`# type: str`). Some of our libraries use type comments due to legacy code supporting Python 2, but these will be updated to annotation style.

A fully annotated signature includes type annotations for all parameters and the return type. The type of a parameter
should follow the `:` syntax and a default argument can be supplied like in the `overwrite` parameter above. A return
type follows the function def with an arrow `->`, its type, and then closes with `:`.

It is also possible to add type annotations to variables. The syntax follows the same as
function arguments:

```python
length: int = 42
width: int = 8
area: int = length * width
```

When typing your library, note that almost anything can be used as a type - basic data types like `str`, `int`, `bool`,
types from the `typing` or `typing_extensions` modules, user-defined types, abstract base classes, and more.
See [Types usable in annotations](#types-usable-in-annotations) for more information.

## Typing a client library

When starting to add type hints to a client library, there are a few things to consider. First, Python has a "gradual
type system". What this means is that typing is not an all-or-nothing task - you can gradually add types into your code
and any code without type hints will just be ignored by the type checker. Typing is optional and this is a good
thing! Pushing to achieve full coverage of annotated code can lead to low signal-to-noise and sometimes is not practical 
given the expressiveness of Python as a language. So, in practice, what should you aim to type?

1) Add type hints to publicly exposed APIs in the client library. Type hints get shipped with our client libraries (both whl and sdist)
   and provide benefit to our users. To ensure that type hints do get shipped in your library and can be checked by a static
   type checker, follow the steps per [PEP 561](https://mypy.readthedocs.io/en/stable/installed_packages.html#creating-pep-561-compatible-packages) below:

    - add an empty `py.typed` file to your package directory. E.g. `.../sdk/azure-core/azure/core/py.typed`
    - include the path to the `py.typed` in the
      MANIFEST.in ([example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/MANIFEST.in)).
      This is important as it ensures the `py.typed` is included in both the sdist/bdist.
    - set `include_package_data=True` and `package_data={"azure.core": ["py.typed"]}` in the setup.py.
      Note that the key should be the namespace of where the `py.typed` file is found.

2) Add type hints anywhere in the source code where unit tests are worth writing. Consider typing/mypy as "free" tests
   for your library so focusing typing on high density/important areas of the code helps in detecting bugs.

## Types usable in annotations

Almost anything can be used as a type in annotations.

1) Basic types like `int`, `str`, `bytes`, `float`, `bool`
2) Classes or abstract base classes - whether user-defined, from the standard library
   like [collections](https://docs.python.org/3/library/collections.html)
   or [collections.abc](https://docs.python.org/3/library/collections.abc.html), or external packages
3) Types from the [typing](https://docs.python.org/3/library/typing.html)
   or [typing_extensions](https://github.com/python/typing/tree/master/typing_extensions) modules
4) Built-in generic types, like `list` or `dict`*.
   > *Note: Supported in Python 3.9+. For <3.9, You must include `from __future__ import annotations` import to be able to pass in generic `list[str]` as a type hint rather than `typing.List[str]`.

Here are a few considerations and notes on Python version support:

- With [PEP585](https://peps.python.org/pep-0585/) and [PEP563](https://peps.python.org/pep-0563/), importing certain
  generic collection types from `typing` has been [deprecated](https://peps.python.org/pep-0585/#implementation) in
  favor for using the types in `collections.abc` or generic collection type hints (like `list`) from the standard library.
  If you'd like to use types from `collections.abc`, you can check the Python version at runtime (`collections.abc` types did not have [] notation / indexing support added until 3.9).

```python
import sys

if sys.version_info < (3, 9):
    from typing import Sequence
else:
    from collections.abc import Sequence
```

- The `typing-extensions` library backports types that are introduced only in later versions of Python (e.g. `Protocol`
  which was introduced in Python 3.8) so that they can be used in earlier Python versions.

```python
from typing_extensions import Protocol
```

If using `typing-extensions`, you must add it to the install dependencies for your library (do not rely on install by `azure-core`)
[[example](https://github.com/Azure/azure-sdk-for-python/blob/5fd52b9ee039f8711322bd7ea43af763d326291a/sdk/eventhub/azure-eventhub/setup.py#L73)].
When importing a backported type into code, `typing-extensions` does a try/except on your behalf (either importing
from `typing` if supported, or `typing-extensions` if the Python version is too old) so there is no need to do this
check yourself.

See the [typing-extensions](https://github.com/python/typing_extensions) docs to check what has been
backported. This document calls out which types are needed through `typing-extensions` based on support of Python 3.7+.
Some commonly used types imported from `typing-extensions` are Literal, TypedDict, Protocol, runtime_checkable, and Final.

## Install and run type checkers on your client library code

Our Python SDK repo CI runs two type checkers on the code - [mypy](https://mypy.readthedocs.io/en/stable/) and [pyright](https://github.com/microsoft/pyright). You may see different errors across type checkers.
We aim for the Python SDK to provide "type checker clean" client libraries whether using mypy or pyright so that our customers are able to choose either and have a good typing experience. The type checkers run
on the client library code and the sample code found under the `samples` directory for your library.

The versions of mypy and pyright that we run in CI are pinned to specific versions in order to avoid surprise typing errors raised when a new
version of the type checker ships. All client libraries in the Python SDK repo are automatically opted in to running type checking. If you need to temporarily opt-out of type checking for your client library, see [How to opt out of type checking](#how-to-opt-out-of-type-checking).

The easiest way to install and run the type checkers locally is
with [tox](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox). This reproduces the exact type checking
environment run in CI and brings in the third party stub packages necessary. To begin, first install `tox` and `tox-monorepo`:

`pip install tox tox-monorepo`

### Run mypy

mypy is currently pinned to version [0.931](https://pypi.org/project/mypy/0.931/).

To run mypy on your library, run the tox mypy env at the package level:

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics>tox -e mypy -c ../../../eng/tox/tox.ini`

If you don't want to use `tox` you can also install and run mypy on its own:

`pip install mypy==0.931`

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics>mypy azure`

Note that you may see different errors if running a different version of mypy than the one in CI.

Configuration of mypy is handled globally for the repo, but if specific configuration of mypy is needed for your library, use a `mypy.ini` file
([example](https://github.com/Azure/azure-sdk-for-python/blob/1c8862a74543dd2a979f3c485c3ae69cef4bc7ee/sdk/textanalytics/azure-ai-textanalytics/mypy.ini)) at the package level:

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics/mypy.ini`

For example, you might want mypy to ignore type checking files under a specific directory:

```md
[mypy-azure.ai.textanalytics._dont_type_check_me.*]
ignore_errors = True
```

Full documentation on mypy config options found here: https://mypy.readthedocs.io/en/stable/config_file.html

### Run pyright

We pin the version of pyright to version [1.1.287](https://github.com/microsoft/pyright).

Note that pyright requires that node is installed. The command-line [wrapper package](https://pypi.org/project/pyright/) for pyright will check if node is in the `PATH`, and if not, will download it at runtime.

To run pyright on your library, run the tox pyright env at the package level:

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics>tox -e pyright -c ../../../eng/tox/tox.ini`

If you don't want to use `tox` you can also install and run pyright on its own:

`pip install pyright==1.1.287`

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics>pyright azure`

Note that you may see different errors if running a different version of pyright than the one in CI.

Configuration of pyright is handled globally for the repo, but if specific configuration of pyright is needed for your library, use a `pyrightconfig.json` file at the package level.

For example, to ignore type checking files under a specific directory, you can use `exclude`:

```json
{
  "exclude": ["**/_dont_type_check_me/**"]
}
```

Full documentation on pyright config options can be found here: https://github.com/microsoft/pyright/blob/main/docs/configuration.md

### Run verifytypes

[verifytypes](https://github.com/microsoft/pyright/blob/main/docs/typed-libraries.md#verifying-type-completeness) is a feature of pyright which measures the type completeness of
a py.typed library. It analyzes all the symbols that are part of the public interface and reports whether that symbol is known (fully typed), unknown, or ambiguous.
The report can be used to view where type hints and docstrings are missing in a library, but differs from mypy/pyright in that it does not judge whether the provided type hints are accurate.
verifytypes also reports a type completeness score which is the percentage of known types in the library. This score is used in the CI check to fail if the type completeness of the library worsens
from the code in the PR vs. the latest release on PyPi.

To run verifytypes on your library, run the tox verifytypes env at the package level:

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics>tox -e verifytypes -c ../../../eng/tox/tox.ini`

If you don't want to use `tox` you can also install and run pyright/verifytypes on its own:

`pip install pyright==1.1.287`

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics>pyright --verifytypes azure.ai.textanalytics --ignoreexternal`


### How to ignore type checking errors

A type checking error can be globally ignored by placing a `# type: ignore` comment on the offending line. Generally, we do not want to
ignore errors if we can, but sometimes it is not possible to fix the error, e.g. there might be bug in the type checker _or_
the Python code is more expressive than the type system allows. If you must ignore an error, it is
recommended that you explain your reasoning in the ignore comment and include a link to the bug or Github issue so someone
reading the code later may resolve it.

*Globally ignore (both mypy and pyright):*
```python
ignore_me: int = 5  # type: ignore  https://www.github.com/Azure/azure-sdk-for-python/issues/my-issue
```

Note that it is possible to be specific in the error to ignore, instead of globally turning off type checking on
that line. Syntax for this involves putting the specific error code in brackets of the ignore comment. Error codes
are found next to the type checking error. 

*mypy:*
```python
ignore_me: int = 5  # type: ignore[misc]
```

*pyright:*
```python
ignore_me: int = 5  # pyright: ignore[reportPrivateUsage]
```

The type checkers will continue to evaluate the line of code for other typing errors.


More information about suppressing errors can be found in the
official [mypy docs](https://mypy.readthedocs.io/en/stable/type_inference_and_annotations.html?highlight=ignore#silencing-type-errors) and [pyright docs](https://github.com/microsoft/pyright/blob/main/docs/comments.md#line-level-diagnostic-suppression).


### How to opt out of type checking

All client libraries in the Python SDK repo are automatically opted in to running type checking. If there is a
reason why a particular library should not run type checking, it is possible to disable mypy/pyright from running in CI.

1) Disable the check in the library's `pyproject.toml` file following the instructions in [doc/eng_sys_checks.md](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md#the-pyprojecttoml).
2) Open an issue tracking that "library-name" should be opted in to running type checking

> Note: Blocking your library from type checking is a *temporary* state. It is expected that checks are re-enabled as soon as possible.

## Typing tips and guidance for the Python SDK

This is not intended to be a complete guide to typing in Python. This section covers some common typing scenarios
encountered when working on the SDK and provides some tips for you to get started. Typing is relatively new to Python,
with over 20 PEPs and counting. Please check the [typing](https://docs.python.org/3/library/typing.html) documentation for the most up-to-date information.

### Use typing.Any sparingly

`typing.Any`, like the name suggests, assumes that a type can be _anything_ - it is compatible with every other type,
and vice versa. This is what allows gradual typing in Python, as an untyped function like this...

```python
def add_things(x, y):
    return x + y
```

is seen by the type checker as this...

```python
from typing import Any


def add_things(x: Any, y: Any) -> Any:
    return x + y
```

`Any` should be used sparingly since it effectively turns the type checker off. If the type can be narrowed down to
something more specific, that is preferred since over usage of `Any` can undermine the type checker's ability to find
bugs in other parts of the code. Additionally, `Any` does not benefit our customers who may be using type checking with
our libraries.

### Use typing.Union when accepting more than one type

[typing.Union](https://docs.python.org/3/library/typing.html#typing.Union) allows for typing something with more than
one type. For example, a Union[str, DocumentBuildMode] means that either `str` or `DocumentBuildMode` are permissible for
the `build_mode` parameter:

```python
from typing import Union


def begin_build_model(
    self, source: str, build_mode: Union[str, DocumentBuildMode], **kwargs: Any
) -> DocumentModelAdministrationLROPoller[DocumentModelInfo]:
    ...
```

A `Union` requires at least two types and should be used with types that are not consistent with each other. For
example, usage of `Union[int, float]` is not necessary since `int` is consistent with `float` (implements all the supported operations of `float`) -- you can just use `float`. It's
also recommended avoiding having functions return `Union` types as it causes the user to need to understand or perform `isinstance` checks
on the return value before acting on it to write type-safe code. Sometimes this can be resolved by using an [overload](#use-typingoverload-to-overload-a-function).

Note that adding support for a `Union` on input is generally non-breaking. However, adding a `Union`
(or additional options to an existing `Union`) for a return type could be considered breaking and such a change should
be brought to the attention of the Python architects.

### Use typing.Optional when a parameter can explicitly be None

Python's typing docs for [Optional](https://docs.python.org/3/library/typing.html#typing.Optional) explain that

> Optional[X] is equivalent to X | None (or Union[X, None])

Optional is just a specialized Union and somewhat confusingly named. `Optional` should only be used when an argument can be either
something _or_ `None`. It should not be used just because a parameter has a default argument. For example, `Optional` usage is appropriate here:

```python
from typing import Optional, Any

def begin_export_project(
    project_name: str,
    *,
    string_index_type: str = "UnicodeCodePoint",  # Param with a default, doesn't allow None, doesn't require Optional
    asset_kind: Optional[str] = None,  # None is allowed, type as Optional
    **kwargs: Any
) -> LROPoller[JSON]:
    ...
```

Per PEP 484, type checkers have moved towards requiring the Optional type to be made explicit when a default of None is provided.

> Note: The `X | None` syntax is only supported in Python 3.10+.

### Typing for collections

A few things to think about when typing collections in Python.

1) We should aim to be lenient in the types we accept as a parameter because this allows for more
   flexibility for the caller, e.g. accepting an `Iterable` (where appropriate) allows for more possible types to be
   passed (list, tuple, dict, etc.) than just specifying a `List`. For return types, since we support APIs which are
   expected to evolve over time, it is also helpful to return more flexible types. So long as our return type
   adheres to a given protocol, we are more likely to not break our user's code.

2) It can be more useful to consider the set of supported operations as the defining characteristic of a type.
   [Structural subtyping](https://en.wikipedia.org/wiki/Structural_type_system) is what supports duck typing in
   Python.

#### Mapping types

Syntax for mapping types follows: `MappingType[Key, Value]`. For example, `typing.Dict[str, str]` indicates that
the type is a dictionary with string keys and string values.

For mapping parameter types, consider using `Mapping` or `MutableMapping`. If the function accepting the mapping
type does not need to mutate the mapping, `Mapping` provides more flexibility than `MutableMapping` (which
implements methods like `pop`, `update`, `clear`).

For example,

```python
from typing import Mapping

def create_table(entity: Mapping[str, str]) -> None:
    ...
```

By accepting `Mapping` here, we give more flexibility to the user and allow them to specify anything consistent
with a `Mapping` - dict, defaultdict, a user-defined dict-like class, or any subtype of `Mapping`. Had we
specified a generic `typing.Dict` here, the `entity` passed must be a `dict` or one of its subtypes, narrowing the types
accepted.

With [PEP 589](https://peps.python.org/pep-0589/), a `TypedDict` was introduced in Python 3.8 which allows you to add
type hints for dictionaries with a fixed set of keys. The syntax for this looks similar to building a dataclass:

```python
# from typing import TypedDict  # Python >= 3.8
from typing_extensions import TypedDict


class Employee(TypedDict):
    name: str
    title: str
    id: int
    current: bool
```

A `TypedDict` lets you specify types hints for the value of each key in the dictionary.
It's important to note that `Employee` has no runtime effect - the interpreter will not validate that the keys or values
passed are the correct types. However, during static type checking, when the `Employee` TypedDict is constructed, the type checker
will expect the keys and typed values specified.

```python
employee = Employee(name="krista", title="swe", id="nah", current=True)
```

mypy identifies that the `id` key is the wrong type:

`main.py:9: error: Incompatible types (expression has type "str", TypedDict item "id" has type "int")`

At runtime, `employee` is perfectly valid even though it does not conform to a true `Employee`:

```cmd
>>>employee = Employee(name="krista", title="swe", ident="nah", current=True)
>>>print(employee)
{'name': 'krista', 'title': 'swe', 'ident': 'nah', 'current': True}
>>>type(employee)
<class 'dict'>
```

Note that this creates a plain `dict` at runtime. Due to this, `TypedDict` cannot be used in `isinstance` checks,
e.g. `isinstance(employee, Employee)` will throw a `TypeError`. Usage of `TypedDict` is a great way to inform the
type checkers and Intellisense how a specific dict should be constructed and help the type checkers warn users if
they try to access keys which don't exist.

Use of generic TypedDict is also supported via typing_extensions (>=4.3.0). For example,

```python
# from typing import TypedDict  # Python >= 3.8
from typing_extensions import TypedDict
from typing import Generic, TypeVar, List

T = TypeVar("T")


class Employee(TypedDict, Generic[T]):
    name: str
    title: str
    id: int
    current: bool
    additional_info: List[T]

employee = Employee[str](name="krista", title="swe", id=123, current=True, additional_info=["Redmond"])
```

See the [TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict) docs for more options.

> Note that TypedDict is backported to older versions of Python by using typing_extensions.

#### List

The [typing.List](https://docs.python.org/3/library/typing.html#typing.List) docs make a recommendation:

> Useful for annotating return types. To annotate arguments it is preferred to use an abstract collection type such as Sequence or Iterable

For iterable parameter types, consider using `Sequence` or `MutableSequence` or plain `Iterable`
depending on the needs the function has for the collection type.

In determining whether to use, for example, `Sequence` or `Iterable` as a parameter type, it's important to understand
the supported operations of each and how much flexibility we can give the caller. A good reference table for the set of
supported operations for generic collections is found
in the [collections.abc docs](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes).
For example, `Iterable` input is flexible in that it can accept a generator as input, whereas `Sequence` is not -- it
must provide the ability to call `len()`.

#### Tuples

Special mention for `Tuple` since there are a few ways to type annotate with it.

Syntax for a tuple may look like: `Tuple[str, int, float]` which may hold an item, quantity, price:

`item = ("pencil", 1, 0.99)`

If the tuple has an arbitrary amount of same type arguments, you can use `...` syntax:

`Tuple[str, ...]`

Additionally, if your tuple has named fields there is `typing.NamedTuple` which can be used as a factory for tuple subclasses:

```python
from typing import NamedTuple, List


class Point(NamedTuple):
    x: float
    y: float


def bounding_box(points: List[Point]) -> None: ...
```

Note that `Point` is consistent with `Tuple[float, float]`, but not vice versa. In other words, you can't pass a
vanilla `Tuple[float, float]` into the `bounding_box` function above, but if it were annotated
as `points: Tuple[float, float]`, a `Point` would be permissible. This is because NamedTuple is a class builder
and may have extra methods or user-defined methods that `Tuple` does not.

### Parameters not needing type annotations

There are some parameters that we do not need to type annotate in the SDK.

The `self` parameter in a class method does not need to be typed. Nor does the `cls` parameter in a `@classmethod`.
However, it is customary to return `None` on a `__init__` like below since this will indicate that it should be
type checked (since there are no other typed parameters found in signature).

```python
class KeyCredential:
    
    def __init__(self) -> None:
        ...
```


### Typing variadic arguments - *args and **kwargs

Many of our client methods take a `**kwargs` and sometimes an `*args` argument.

Consider the below example:

```python
def begin_operation(*args, **kwargs) -> None:
    ...
```

Assume that `*args` accepts an arbitrary number of positional parameters which must be of type `str`. Let's
also assume that `**kwargs` accepts operation-specific keyword arguments, including any `azure-core` specific keyword
arguments. In this case, we can narrow the type for `*args` to `str`. For `**kwargs`, due to the complexity of the type,
we will leave it as `Any` (one day this might be solved by [PEP 692](https://peps.python.org/pep-0692/)). Typed this looks like:

```python
from typing import Any


def begin_operation(*args: str, **kwargs: Any) -> None:
    ...
```

Note how mypy understands these types:

```cmd
main.py:4: note: Revealed local types are:
main.py:4: note:     args: builtins.tuple[builtins.str]
main.py:4: note:     kwargs: builtins.dict[builtins.str, Any]]"
```

mypy correctly infers `*args` as a `tuple[str]` and `**kwargs` as a `dict[str, Any]` so we do not need to type these
as such in the code. If `*args` accepts more than just `str`, a `Union[]` type can be used.

### Use TYPE_CHECKING to avoid circular imports

`typing.TYPE_CHECKING` is a constant that is evaluates to `True` when type checkers are running, but is otherwise `False` at
runtime. A common instance of when you might need to use `TYPE_CHECKING` is when a circular import is created due to
imports necessary for type annotations:

a.py

```python
from b import Baz


def create_foo(b: Baz) -> None:
    b.hello()


def bar() -> None:
    print("bar")
```

b.py

```python
from a import bar


class Baz:
    def hello(self) -> None:
        bar()
```

Here `a` imports from `b` and `b` imports from `a`, causing a circular import at runtime:

`ImportError: cannot import name 'Baz' from partially initialized module 'b' (most likely due to a circular import)`

Since `TYPE_CHECKING` is only `True` when running the type checker, we can add our imports under a TYPE_CHECKING block
to fix this issue in a.py:

a.py

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from b import Baz


def foo(b: "Baz") -> None:
    b.hello()


def bar() -> None:
    print("bar")
```

Note that we also had to change Baz to a forward reference since it will not be defined at runtime under
the `TYPE_CHECKING` conditional.

Another reason to use `TYPE_CHECKING` is to hide importing types which are needed only for type annotations and are
costly to load at runtime. That being said, types imported from `typing` or `typing_extensions` do not need to be put inside
a `TYPE_CHECKING` conditional.

### Passing a function or a class as a parameter or return type

`typing.Callable` can be used to annotate callback parameters or functions returned by higher-order functions. Syntax as
follows: `Callable[[ParamType1, ParamType2, ...], ReturnType]`

The argument list must be a list of types and have a single type for the return type. Currently, there is no way to annotate optional or keyword arguments. If this is needed, replace the entire ParamType list with `...`:

`Callable[..., ReturnType]`

```python
from typing import Callable


def add(x: int, y: int) -> int:
    return x + y


def multiply(x: int, y: int) -> int:
    return x * y


def do_math(op: Callable[[int, int], int], x: int, y: int) -> int:
    return op(x, y)


product = do_math(multiply, 2, 2)
sum = do_math(add, 2, 2)
```

Type annotations for class objects differ from type annotations for class instances.

In the below example, `make_quack` accepts an initialized `Duck` while `create_duck` accepts a class object of `Duck`.
The former can be written as `Duck` while the latter should be written as `typing.Type[Duck]` to indicate this
difference.

```python
from typing import Type


class Duck:
    def quack(self): ...


def make_quack(d: Duck) -> None:
    d.quack()


def create_duck(d: Type[Duck]) -> Duck:
    return d()


d = Duck()
make_quack(d)  # OK
create_duck(d)  # mypy complains

make_quack(Duck)  # mypy complains
create_duck(Duck)  # OK
```

Running mypy shows the expected output:

```cmd
main.py:15: error: Argument 1 to "create_duck" has incompatible type "Duck"; expected "Type[Duck]"
main.py:17: error: Argument 1 to "make_quack" has incompatible type "Type[Duck]"; expected "Duck"
Found 2 errors in 1 file (checked 1 source file)
```

### Use forward references when a type does not exist yet

Sometimes you might want to use a type in a type hint which hasn't been defined yet. This is commonly encountered when using `@classmethod` and we see Python complain at runtime.

```python
class TreeHouse:
    def __init__(self): ...

    @classmethod
    def build(cls) -> TreeHouse:
        return cls()
```

```cmd
    class TreeHouse:
  File "testing_mypy.py", line 12, in TreeHouse
    def build(cls) -> TreeHouse:
NameError: name 'TreeHouse' is not defined
```

You can fix this in a few ways, the most simple and recommended way is to use a forward reference which involves wrapping
the return type in a string:

```python
class TreeHouse:
    def __init__(self): ...

    @classmethod
    def build(cls) -> "TreeHouse":  # forward reference
        return cls()
```

Type checkers understand forward references and will treat this as the actual type when type checking.


A second way is with usage of the import `from __future__ import annotations`:

```python
from __future__ import annotations

class TreeHouse:
    def __init__(self) -> None: ...

    @classmethod
    def build(cls) -> TreeHouse:
        return cls()
```

Since the behavior of this import is subject to change in the future (see [PEP 649](https://peps.python.org/pep-0649/)),
it is recommended to use a forward reference to solve this for now.

At import time, the default behavior in Python is to read in all type hints and store them in `__annotations__` as their actual types.
`from __future__ import annotations` changes this such that type hints don't get evaluated at runtime and are preserved as string literals in the `__annotations__` dictionary.
There is no difference in behavior for the type checkers with using this import. Note that `from __future__ import annotations` must be imported at the top of the file before any other imports.

It's also worth calling out that using this import also allows use of generic collection type hints like `dict` and `list` instead of `typing.Dict` and `typing.List`. 

More details about this import and its behavior can be found in [PEP 563](https://peps.python.org/pep-0563/). Information
about the PEP which may supersede this can be found in [PEP 649](https://peps.python.org/pep-0649/).

### Use type aliases to create readable names for types

Use a type alias to create more readable types or convey intent.

```python
from typing import List, Tuple, Dict

Coordinate = Tuple[float, float]
Route = List[Coordinate]
TrailName = str
Trails = Dict[TrailName, Route]


def get_trails(state) -> Trails:
    ...

# vs.

def get_trails(state) -> Dict[str, List[Tuple[float, float]]]:
    ...
```

If it's possible that a type alias could be confused with a global assignment, e.g. `x = 1`, you can use `typing.TypeAlias`.
This removes ambiguity for the type checker and indicates this isn't a normal variable assignment.

```python
# from typing import TypeAlias Python >=3.10
from typing_extensions import TypeAlias

x: TypeAlias = 1
```

> Note that TypeAlias is backported to older versions of Python by using typing_extensions.

### Use typing.overload to overload a function

`typing.overload` allows for annotating different combinations of typed arguments for a function. This can be useful when the
return type might depend on the type or types of parameters.

Consider a function which takes in different input types which then inform the output type:

```python
from typing import Union


def analyze_text(text: str, analysis_kind: Union[SentimentAnalysis, EntityRecognition, LanguageDetection]) -> Union[
    SentimentResult, EntityRecognitionResult, LanguageDetectionResult]:
    return _analyze(text, analysis_kind)
```

We can annotate this function with overloads to help inform the type checker which input maps to
which return type.

```python
from typing import overload, Union


@overload
def analyze_text(text: str, analysis_kind: LanguageDetection) -> LanguageDetectionResult:
    ...

@overload
def analyze_text(text: str, analysis_kind: EntityRecognition) -> EntityRecognitionResult:
    ...

@overload
def analyze_text(text: str, analysis_kind: SentimentAnalysis) -> SentimentResult:
    ...

# actual implementation
def analyze_text(text: str, analysis_kind: Union[SentimentAnalysis, EntityRecognition, LanguageDetection]) -> Union[
    SentimentResult, EntityRecognitionResult, LanguageDetectionResult]:
    return _analyze(text, analysis_kind)
```

Running mypy shows that the correct return type is inferred from the input type:

```python
result = analyze_text("my text", LanguageDetection())
reveal_type(result)
```

`main.py:28: note: Revealed type is "__main__.LanguageDetectionResult"`

`typing.overload` can also be used when there are a different number of typed arguments or when wanting to present
optional parameters as required, or vice versa. We can take the above example and imagine that `analyze_text` has an
additional overload which does not take an `analysis_kind` (note that we switched to accepting `*args` and `**kwargs`
in the actual implementation for this case):

```python
from typing import overload, Union, Any


@overload
def analyze_text(text: str, analysis_kind: LanguageDetection) -> LanguageDetectionResult:
    ...


@overload
def analyze_text(text: str, analysis_kind: EntityRecognition) -> EntityRecognitionResult:
    ...


@overload
def analyze_text(text: str, analysis_kind: SentimentAnalysis) -> SentimentResult:
    ...


@overload
def analyze_text(text: str) -> str:
    ...

# actual implementation
def analyze_text(*args: Union[str, LanguageDetection, EntityRecognition, SentimentAnalysis], **kwargs: Any) -> Union[str, SentimentResult, EntityRecognitionResult, LanguageDetectionResult]:
    # logic parsing args / kwargs
    ...
```

Running mypy again shows that it understands the return types based on the different number of arguments:

```python
language_result = analyze_text("my text", LanguageDetection())
reveal_type(language_result)

text_result = analyze_text("my text")
reveal_type(text_result)
```

```cmd
main.py:36: note: Revealed type is "__main__.LanguageDetectionResult"
main.py:39: note: Revealed type is "builtins.str"
```

An overload needs two or more variants + the actual implementation to be valid. Because the implementation is the only
function allowed to contain code, you must handle the different combinations of arguments at runtime yourself in order 
to create the desired behavior.

### Use typing.cast to help the type checker understand a type

Sometimes the type checkers will be unable to infer a type and may raise a false positive error. Using `typing.cast` is a way to
tell the checker what the type of something is and is generally favored over using a `# type: ignore`.

The below snippet shows an example of how mypy might need a little help to understand the parameter type specified in
a union:

```python
from typing import Union, List, Optional, Any, cast


def receive_deferred_messages(
        self, sequence_numbers: Union[int, List[int]], *, timeout: Optional[float] = None, **kwargs: Any
) -> List[ServiceBusReceivedMessage]:
    if isinstance(sequence_numbers, int):
        sequence_numbers = [sequence_numbers]
    sequence_numbers = cast(List[int], sequence_numbers)  # mypy clarity

    for num in sequence_numbers:  # if not cast to List[int], mypy will error
        print(num)
```

If you are using cast often, it might be an indication that the code should be otherwise written or refactored.
Note that `typing.cast` is only used by the type checker and does not affect code or slow down the implementation at
runtime.

### Use typing.TypeVar and typing.Generic for generic type hinting

`TypeVar` is a generic type which can be bound to a specific type with each usage. Common usage might be to have the
parameter type reflected on the result type:

```python
from typing import Sequence, TypeVar

T = TypeVar("T")


def pick(p: Sequence[T]) -> T:
    return random_pick(p)
```

This leaves the type open for the caller to pass a `Sequence[int]`, `Sequence[float]`, `Sequence[str]`, etc. and
promises to return the same `T` type passed in. A TypeVar can be constrained or bound to certain types.

**Set the upper bound on a TypeVar**

Another way to narrow the type of a `TypeVar` is to provide the `bound` keyword argument with a type which should be
considered the upper boundary of `T`, or a subtype of `T`. Here we pass `typing.SupportsFloat` which says that anything passed as `T` should
be consistent with `SupportsFloat` and must implement `__float__`.

```python
from typing import Sequence, TypeVar, SupportsFloat

T = TypeVar("T", bound=SupportsFloat)


def pick(p: Sequence[T]) -> T:
    return random_pick(p)
```

Note that is recommended to use `bound` over constraining a `TypeVar` with several types:

```python
from typing import TypeVar, Union

S = TypeVar("S", bound=Union[int, str])  # Yes

T = TypeVar("T", int, str)  # No, can have unexpected behavior
```


**Use typing.TypeVar with typing.Generic to create a generic class**

You can also use `TypeVar` with `typing.Generic` to create user-defined generic classes. Generics let you create a class
which can be used with multiple types -- the type is just stated when the class is instantiated. After instantiation,
the instance will only allow arguments of that type and it will be type checked as such. An example
is [azure.core.polling.LROPoller](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/polling/_poller.py#L144)
. The abbreviated snippet of its definition below shows that it is defined as a generic class that takes a single type
parameter `PollingReturnType` which can then be used to type throughout the implementation.

```python
from typing import TypeVar, Generic, Callable, Any, Optional

PollingReturnType = TypeVar("PollingReturnType")


class LROPoller(Generic[PollingReturnType]):
    def __init__(self, client: Any, initial_response: Any, deserialization_callback: Callable,
                 polling_method: PollingMethod[PollingReturnType]):
        ...

    def result(self, timeout: Optional[int] = None) -> PollingReturnType:
        ...
```

When creating an instance of LROPoller, the actual type parameter is passed in `[]`, e.g. here `PollingReturnType` is
equal to `Dict[str, str]`:

```python
from typing import Dict
from azure.core.polling import LROPoller

poller = LROPoller[Dict[str, str]](client, initial_response, deserialization_callback, polling_method)
reveal_type(poller)

result = poller.result()
reveal_type(result)
```

mypy output:

```cmd
main.py:93: note: Revealed type is "azure.core.polling._poller.LROPoller[builtins.dict[builtins.str, builtins.str]]"
main.py:96: note: Revealed type is "builtins.dict[builtins.str, builtins.str]"
```

If the actual type parameter is not passed when LROPoller is declared, the type checker will infer the `PollingReturnType` as `Any`.

Note that is redundant to type a class with `Generic`, when it already subclasses another generic type and specifies
type variables, like in the `azure.core.paging` implementation
of [ItemPaged](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/paging.py#L91)
which subclasses `Iterator` with a type variable:

```python
from typing import Iterator, TypeVar

ReturnType = TypeVar("ReturnType")


class ItemPaged(Iterator[ReturnType]):
    ...
```

There are arguments available to set the variance in a `TypeVar` for the generic class to be more flexible -- please
see [PEP 484](https://peps.python.org/pep-0484/#covariance-and-contravariance) for more information.

See more on `Generic` in the [reference docs](https://docs.python.org/3/library/typing.html#user-defined-generic-types).

### Use AnyStr when your parameter or return type expects both str and bytes

The `typing` module includes a pre-defined `TypeVar` named `AnyStr`. Its definition looks something like this:

```python
from typing import TypeVar

AnyStr = TypeVar('AnyStr', bytes, str)
```

`AnyStr` can be indicated in functions which use both `bytes` and `str` and helps keep consistent typing across
arguments / return type:

```python
def concat(a: AnyStr, b: AnyStr) -> AnyStr:
    return a + b
```

If passing `bytes` for parameter `a` in the above function, note that `bytes` must be passed for both `b` and the return type. Mixing `bytes` and `str` will result in error:

```python
res = concat(b'hello', 'world')  # mixing bytes and str
```

mypy output:

```cmd
main.py:6: error: Value of type variable "AnyStr" of "concat" cannot be "Sequence[object]"
```


### Use typing.Protocol to support duck typing

[PEP 544](https://peps.python.org/pep-0544/) introduced the `Protocol` type. The `Protocol` type helps Python support
structural subtyping or "static duck typing". In other words, when looking at whether two types are compatible, the
actual structure and capabilities are what matters.

A `Protocol` type can be defined by one or more methods, and a type checker will check that those methods are
implemented where a protocol type is specified.

Below we create a `SupportsFly` protocol class which expects a `fly()` method on all compatible types being passed
into `ascend()`.

```python
# from typing import Protocol  # Python >=3.8
from typing_extensions import Protocol


class SupportsFly(Protocol):
    def fly(self) -> None: ...


class Butterfly:
    def fly(self) -> None: ...

    def sunbathe(self) -> None: ...


class Plane:
    def fly(self) -> None: ...


class Penguin:
    def waddle(self) -> None: ...


def ascend(f: SupportsFly) -> None:
    f.fly()


p = Plane()
ascend(p)  # OK

b = Butterfly()
ascend(b)  # OK

g = Penguin()
ascend(g)  # Mypy complains below
```

Running mypy shows expected output:

```cmd
main.py:23: error: Argument 1 to "ascend" has incompatible type "Penguin"; expected "SupportsFly"
Found 1 error in 1 file (checked 1 source file)
```

Because Penguin does not implement the `SupportsFly` Protocol is called out as an incompatible type. However, any type
that is consistent with, or implements all the methods defined by the `SupportsFly` protocol, is acceptable to pass
into `ascend()`.

A key difference between Protocols and abstract classes (abc) is that protocols work at typing time while abcs work at
runtime. A class does not need to _inherit_ from Protocol like an abc, the type checker will simply enforce its usage at
typing time.

A common Python SDK Protocol type we use
is [azure.core.credentials.TokenCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/credentials.py)
. TokenCredential requires that a type implements the `get_token` method for it to be consistent with the Protocol.

See more on Protocols in the [reference documentation](https://docs.python.org/3/library/typing.html#typing.Protocol).

#### Use runtime_checkable to do simple, runtime structural checks on Protocols

If a Protocol is marked with @runtime_checkable, it can be used with `isinstance()` and `issubclass()` at runtime.

```python
# from typing import runtime_checkable  Python >=3.8
from typing_extensions import runtime_checkable, Protocol


@runtime_checkable
class SupportsFly(Protocol):
    def fly(self) -> None: ...


assert isinstance(Plane, SupportsFly)  # True
assert isinstance(Penguin, SupportsFly)  # False
```

Because this is a runtime check, only the presence of the required methods defined by the Protocol is checked -- not
their type signatures.

> Note that runtime_checkable is backported to older versions of Python by using typing_extensions.

### Use typing.Literal to restrict based on exact values

[PEP 586](https://peps.python.org/pep-0586/) introduced the `typing.Literal` type which can be used to indicate that an
expression has a literal specific value. A Literal can contain one or more literal bool, int, str, bytes, or enum
values:

```python
# from typing import Literal  Python >=3.8
from typing_extensions import Literal

doc_type = Literal["prebuilt-receipt"]
allowed_content_types = Literal["application/json", "text/plain", "image/png", "image/jpeg"] 
```

Literals can be useful with functions that behave differently based on an exact value that the caller specifies.

Consider a function with a signature like this:

```python
from typing import Union


def get_element(kind: str) -> Union[SelectionMark, FormWord, FormLine]:
    ...
```

We want to overload this function since the input informs the output type, but since `str` is accepted for each
variation, the type checker can't distinguish the difference:

```python
from typing import overload

@overload
def get_element(kind: str) -> SelectionMark:
    ...


@overload
def get_element(kind: str) -> FormWord:
    ...


@overload
def get_element(kind: str) -> FormLine:
    ...


def get_element(kind):
    ...


s = get_element(kind="selectionMark")
w = get_element(kind="word")
l = get_element(kind="line")

reveal_type(s)
reveal_type(w)
reveal_type(l)
```

mypy output:

```cmd
main.py:34: error: Overloaded function signature 2 will never be matched: signature 1's parameter type(s) are the same or broader
main.py:38: error: Overloaded function signature 3 will never be matched: signature 1's parameter type(s) are the same or broader
main.py:38: error: Overloaded function signature 3 will never be matched: signature 2's parameter type(s) are the same or broader
main.py:49: note: Revealed type is "__main__.SelectionMark"
main.py:50: note: Revealed type is "__main__.SelectionMark"
main.py:51: note: Revealed type is "__main__.SelectionMark"
```

To solve this issue, we can update the `get_element` function to have overloads based on their Literal `kind`:

```python
from typing_extensions import Literal, overload


@overload
def get_element(kind: Literal["selectionMark"]) -> SelectionMark:
    ...


@overload
def get_element(kind: Literal["word"]) -> FormWord:
    ...


@overload
def get_element(kind: Literal["line"]) -> FormLine:
    ...


def get_element(kind):
    ...


s = get_element(kind="selectionMark")
w = get_element(kind="word")
l = get_element(kind="line")

reveal_type(s)
reveal_type(w)
reveal_type(l)
```

mypy output:

```cmd
main.py:50: note: Revealed type is "__main__.SelectionMark"
main.py:51: note: Revealed type is "__main__.FormWord"
main.py:52: note: Revealed type is "__main__.FormLine"
```

`typing.Literal` can also be used to discriminate between types in Unions such that a user is not resigned to
making `isinstance` checks to understand the result. The following example shows a function `get_element` which returns
a Union of types which each contain a discriminator property, `kind`, typed as a Literal.

```python
from typing import Union
from typing_extensions import Literal


# client library code
class SelectionMark:

    def __init__(self):
        self.kind: Literal["selectionMark"] = "selectionMark"
        self.state = "selected"


class FormWord:

    def __init__(self):
        self.kind: Literal["word"] = "word"
        self.word = "hello"


class FormLine:

    def __init__(self):
        self.kind: Literal["line"] = "line"
        self.line = "hello world"


def get_element() -> Union[SelectionMark, FormWord, FormLine]:
    ...


# user code
ele = get_element()

if ele.kind == "selectionMark":
    print(ele.state)
elif ele.kind == "word":
    print(ele.word)
elif ele.kind == "line":
    print(ele.line)
```

The above example requires only simple string comparison by the user and is valid by the type checker. If we replace the `Literal`
typing and type each `kind` as `str`, mypy complains:

```cmd
main.py:37: error: Item "FormWord" of "Union[SelectionMark, FormWord, FormLine]" has no attribute "state"
main.py:37: error: Item "FormLine" of "Union[SelectionMark, FormWord, FormLine]" has no attribute "state"
main.py:39: error: Item "SelectionMark" of "Union[SelectionMark, FormWord, FormLine]" has no attribute "word"
main.py:39: error: Item "FormLine" of "Union[SelectionMark, FormWord, FormLine]" has no attribute "word"
main.py:41: error: Item "SelectionMark" of "Union[SelectionMark, FormWord, FormLine]" has no attribute "line"
main.py:41: error: Item "FormWord" of "Union[SelectionMark, FormWord, FormLine]" has no attribute "line"
```

This puts additional burden on the user and requires them to use `isinstance` checks to make the type checker happy:

```python
ele = get_element()

if isinstance(ele, SelectionMark):
    print(ele.state)
elif isinstance(ele, FormWord):
    print(ele.word)
elif isinstance(ele, FormLine):
    print(ele.line)
```

Therefore, it is preferred to use `typing.Literal` in this situation to provide the best type checking experience for our users.

> Note that Literal is backported to older versions of Python by using typing_extensions.

### Use typing.NewType to restrict a type to a specific context

`NewType` can be useful to catch errors where a particular type is expected. `NewType` will take an existing type and 
create a brand new type in the same shape; however, these two will not be interchangeable. In the below example,
a string should be passed into `print_log`, but that input string should be specifically the type `str` returned from the `sanitize` function.
`NewType` creates a `Sanitized` type which is viewed as a distinct type for the type checker:

```python
from typing import NewType

Sanitized = NewType("Sanitized", str)


def sanitize(log) -> Sanitized:
    return Sanitized(_sanitize(log))

def print_log(log: Sanitized) -> None: ...
```

This helps express intent and also gives the type checker a chance to catch logic errors. For example, if a regular string
is passed, like `print_log("my secret")`, mypy complains:

```cmd
main.py:11: error: Argument 1 to "print_log" has incompatible type "str"; expected "Sanitized"
Found 1 error in 1 file (checked 1 source file)
```

At runtime, `NewType` will return an object that returns its argument when called. Note that `NewType` is not the same as a type alias. A type alias _is_ interchangeable with the type assigned and just provides another name for it.

### Use typing.Final and @final to restrict types from changes

`Final` indicates to the type checker that a variable cannot be re-assigned to a different value (or overridden in a subclass).
It is best used when a variable's scope spans a large amount of modules and you want to ensure that it stays immutable (i.e. no line of code tries to change it).

```python
# from typing import Final  Python >=3.8
from typing_extensions import Final

MAX_BLOB_SIZE: Final = 4 * 1024 * 1024
```

If `MAX_BLOB_SIZE` gets reassigned somewhere else in the code, the type checker will complain:

```cmd
main.py:6: error: Cannot assign to final name "MAX_BLOB_SIZE"
Found 1 error in 1 file (checked 1 source file)
```

Additionally, If you have a method that should not be overridden or a class that should not be subclassed, consider decorating with `@final`.

```python
from typing_extensions import final

class BlobClient:
    @final
    def download(self) -> None:
        ...
```


### Debug type checking with reveal_type and reveal_locals

Sometimes the type checker might raise an error that is difficult to understand -- luckily it is possible to "debug" the type checker and
see what it is thinking / what types it is inferring.
`reveal_type(expr)` and `reveal_locals()` are debugging functions recognized by type checkers. `reveal_type(expr)` can be
placed in code and will tell you the inferred static type of an expression.
`reveal_locals()` can also be placed on any line and will tell you the inferred types of all local variables.

```python
a = [1]  #  `int` type is inferred
reveal_type(a)

c = [1, 'a']  # `int` and `str` are not "duck type" compatible, so type is narrowed to `object`
reveal_type(c)


def hello_world(message: str) -> None:
    print(f'Hello world! {message}')
    reveal_locals()


reveal_type(hello_world)
```

Running mypy on the above reveals the types that mypy sees:

```cmd
main.py:2: note: Revealed type is "builtins.list[builtins.int*]"
main.py:5: note: Revealed type is "builtins.list[builtins.object*]"
main.py:9: note: Revealed local types are:
main.py:9: note:     message: builtins.str
main.py:11: note: Revealed type is "def (message: builtins.str)"
```

These debugging functions don't need to be imported from anywhere and are only recognized by the type checkers - therefore you will
need to remove them from code before runtime.

## Additional Resources

Typing docs: https://docs.python.org/3/library/typing.html

Mypy docs: https://mypy.readthedocs.io/en/stable/

Pyright docs: https://github.com/microsoft/pyright/tree/main/docs

Typing PEPs: https://docs.python.org/3/library/typing.html#relevant-peps

Typing school: https://github.com/python/typing/discussions
