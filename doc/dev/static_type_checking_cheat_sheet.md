# Static Type Checking Cheat Sheet

This cheat sheet details guidance for typing as it relates to the Python SDK. Use your own judgment to achieve the best balance of clarity and flexibility for your Python client library. 

### General guidance

- Do provide type annotations (per [PEP 484](https://peps.python.org/pep-0484/)) to public APIs in the client library.
- You do not need to annotate internal functions in a client library, but you should provide type hints where unit tests are worth writing or where type annotations will assist in understanding of the code.
- Do not use comment style type hints. Use inline, annotation style.
  
```python
# No:
def create_table(table_name):
    # type: (str) -> Table
    ...

# Yes:
def create_table(table_name: str) -> Table:
    ...
```

- Do fully annotate function signatures - this includes type annotations for all parameters and the return type.
- Do fully annotate function signatures in all samples - this ensures the type checks will check the sample code.
- You should annotate variables if the type in the code is different from expected, provides more value than what is already provided by Python itself, or if the type checker requires it.

```python
# No:
table_name: str = "mytable"  # I can tell it's a string, not necessary
create_table(table_name)

# Yes:
table_map: dict[str, Table] = {}  # clarifies what the dictionary expects
table_map[table_name] = create_table(table_name)
```

- You do not need to annotate `self` or `cls`.
- Do return `None` from a constructor.
  
```python
# No:
class KeyCredential:

    def __init__(self):
        ...  # I do not get type checked

# Yes:
class KeyCredential:

    def __init__(self) -> None:
        ...
```

- Do provide type annotations for all public instance variables on a model. Do this by adding class-level type hints
per [PEP526](https://peps.python.org/pep-0526/).

```python
class Tree:
    """Represents a tree.

    :param str location: The location for the tree.
    :param int num_branches: The number of branches on the tree
    :param str kind: The kind of tree.
    
    Note: :ivar: docstrings are redundant since these vars/types are captured below
    """

    location: str
    """A description of the location of the tree."""
    num_branches: int
    """Number of branches on tree."""
    kind: str = "oak"
    """The kind of tree."""

    def __init__(self, *, location: str, num_branches: int, kind: Optional[str] = None) -> None:
        if kind: 
            self.kind = kind
        self.location = location
        self.num_branches = num_branches
```

- Do use [mypy](https://mypy.readthedocs.io/en/stable/) and [pyright](https://github.com/microsoft/pyright) type checkers to statically type check your client library code.
- Do use [black](https://pypi.org/project/black/) to format type annotations.
- Do add type hints directly to the source code. If you think you need to use stub files, check with the architects. Note that with stub files, type checking will only work for _users_ of the stub, but won't type check the library code itself.
- Do mark your client library package to distribute type hints according to [PEP 561](https://peps.python.org/pep-0561/).
- Do use the latest typing features available. If not supported by older versions of Python, consider taking a dependency and importing from `typing-extensions`.

```python
# from typing import TypedDict Python >3.8
from typing_extensions import TypedDict
```

### Importing types

- Do use only publicly exposed client library types in type hints. 
- Do import types from modules such as `typing`, `typing_extensions`, `collections`, and `collections.abc`(Note that indexing support for generic collection types from `collections.abc` is only supported on Python 3.9+).
- Do not import regular type hints under a `typing.TYPE_CHECKING` block. You may use `TYPE_CHECKING` to fix a circular import or avoid importing a type only needed in type annotations that is otherwise costly to load at runtime.

```python
from typing import TYPE_CHECKING

# No:
if TYPE_CHECKING:
    from typing import Union, TypeVar, Any


# Yes:
if TYPE_CHECKING:
    from a import b  # avoiding a circular import
    from expensive import c  # avoiding runtime costs
```

### Ignoring type checkers

- Do not silence the type checker with `type: ignore` unless other options are exhausted. Consider first using `typing.cast` or refactoring the code.
- If you must use a `type: ignore`, try to be specific in what error code you're ignoring.

```python
# mypy ignores only the error code in brackets
ignore_me: int = 5 # type: ignore[misc] 

# pyright ignores only the error code in brackets
ignored = result._private # pyright: ignore[reportPrivateUsage]

# all errors ignored by both mypy and pyright
class Foo(Any): # type: ignore
   ...
```

- Do leave a comment with a link or explanation for the ignore so that it may be fixed later.
- If you need to ignore type checking all files under a directory for your library, use a `mypy.ini` and `pyrightconfig.json` at the package-level.
- If you must opt-out of all type checking temporarily, open an issue to re-enable type checking for your library.
- Try not to use `typing.Any` if it is possible to be more specific. `Any` essentially turns off type checking.

### Unions

- Use `typing.Union` when a parameter can accept more than one type.
  
```python
from typing import Union


def begin_build_model(
    self, source: str, build_mode: Union[str, DocumentBuildMode], **kwargs: Any
) -> DocumentModelAdministrationLROPoller[DocumentModelInfo]:
    ...
```

- Try not using `Union` as a return type since this typically makes the user need to do `isinstance` checks. See if `@overload` can be used to improve the typing experience.
- Do mark a parameter as explicitly `Optional` if a value of `None` is allowed. `Optional` is the same as `Union[<type>, None]`.

```python
from typing import Optional

# Yes:
def foo(
    bar: Optional[str] = None,
) -> None:
    ...

# No:
def foo(
    bar: str = None,
) -> None:
    ...
```

### Collections

- Do familiarize yourself with the supported operations of various abstract collections in the [collections.abc](https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes) docs.
- Do specify type parameters for collection types. If not specified, these will be assumed as `Any`.

```python
# No:
def get_entity(entity_id) -> dict:  # seen by type checker as dict[Any, Any]
    ...

# Yes:
def get_entity(entity_id: str) -> dict[str, str]:
    ...
```

- Do try to be lenient in what you accept as a parameter. For example, typing a parameter as accepting `Sequence` over `List`, or `Mapping` over `Dict` gives more flexibility to the caller.
- Do ensure that the type hint given supports the set of operations needed in the function body.

```python
from typing import Sequence, Iterable

# Yes:
def create_batch(entities: Sequence[Entity]) -> None:
    if len(entities) > 1:
        ...

# No: the function calls len(), Iterable doesn't support it
def create_batch(entities: Iterable[Entity]) -> None:
    if len(entities) > 1:
        ...
```

- If you don't need to mutate the collection, prefer parameter types `Sequence` over `MutableSequence`, `Mapping` over `MutableMapping`, etc.
- Consider using `typing.TypedDict` if a dictionary has a fixed set of keys. This is especially useful if a user needs to construct the dict. Do make this importable from the public namespace.
- Consider using `typing.NamedTuple` if your tuple should have named fields. Do make this importable from the public namespace.


### Overloads

- Use `typing.overload` if your function takes different combinations of typed arguments and the input arguments might inform the return type.

```python
from typing import overload, Union


@overload
def analyze(text: str, task: LanguageDetection) -> LanguageDetectionResult:
    ...

@overload
def analyze(text: str, task: EntityRecognition) -> EntityRecognitionResult:
    ...

@overload
def analyze(text: str, task: SentimentAnalysis) -> SentimentResult:
    ...

# actual implementation
def analyze(
    text: str, task: Union[SentimentAnalysis, EntityRecognition, LanguageDetection]
) -> Union[SentimentResult, EntityRecognitionResult, LanguageDetectionResult]:
    return _analyze(text, task)
```

- You should add type hints to the actual implementation for overloads. This helps with our internal tooling and ensures the implementation is type checked.

### Variadic arguments

- Do include type hints for variadic arguments, like `*args` and `**kwargs`.

```python
from typing import Any

# args seen as tuple[str] by type checker
# kwargs seen as dict[str, Any] by type checker
def begin_operation(*args: str, **kwargs: Any) -> None:
    ...
```

### Forward declarations

- Prefer using a simple forward reference when you need to use a type that is not defined yet in a type hint.

```python
class Triangle:

    @classmethod
    def from_shape(cls) -> "Triangle":  # type checkers understand this as the actual type
        ...
```

### Structural subtyping / Protocols

- Do support the "duck typing" of Python with `typing.Protocol`.
- Mark your `Protocol`s as `@runtime_checkable` so users can use them in `isinstance` and `issubclass` checks.

```python
from typing_extensions import Protocol, runtime_checkable

@runtime_checkable
class TokenCredential(Protocol):
    """Protocol for classes able to provide OAuth tokens."""

    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        ...
```

### Generics

- Use `typing.TypeVar` to let functions/classes work with arguments of any type and retain relationships between arguments and their return values.

```python
from typing import TypeVar, Sequence, Any

# No:
def choose(items: Sequence[Any]) -> Any:
    ...

# Yes:
T = TypeVar("T")

def choose(items: Sequence[T]) -> T:
    ...
```

- Try to constrain your `TypeVar`'s by using the `bound` keyword argument.

```python
from typing import TypeVar

S = TypeVar("S", bound=str)  # limited to str or any subtype of str
```

- Do subclass `typing.Generic` or a generic collection type if your class needs to work with multiple types.
- Do give your `typing.TypeVar`'s descriptive names if they will be publicly exposed in the code.

```python
from typing import TypeVar, Generic

# No:
T = TypeVar("T")

class LROPoller(Generic[T]):
    ...

# Yes:
PollingReturnType = TypeVar("PollingReturnType")

class LROPoller(Generic[PollingReturnType]):
    ...
```

- Follow naming conventions for covariant (`*_co`) and contravariant (`*_contra`) `TypeVar` parameters when setting variance for generic classes.

```python
from typing import TypeVar

T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
```

- Use the pre-defined TypeVar, `typing.AnyStr`, when your parameter or return type expects both `str` or `bytes`.
- Do use `typing.ParamSpec` (a specialized TypeVar) to forward your function type hints from one callable to another callable (e.g. decorators). This preserves type hinting in the original function.

```python
from typing import TypeVar, Callable, ParamSpec


T = TypeVar("T")
P = ParamSpec("P")

def validate_table(func: Callable[P, T]) -> Callable[P, T]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        # validate table
        return func(*args, **kwargs)
    return inner


@validate_table
def create_table(table_name: str, **kwargs: Any) -> None:
    ...
```


### Type Aliases

- Do use type aliases to help make lengthy, complicated type hints more readable or help convey meaning to the reader.

```python
from typing import Union, Dict
from azure.core.credentials import AzureKeyCredential, TokenCredential, AzureSasCredential

CredentialTypes = Union[AzureKeyCredential, TokenCredential, AzureSasCredential, Dict[str, str]]  # PascalCase
```

- Do not use type aliases in docstrings. Specify the fully expanded type to satisfy rendered documentation.
- Do use `typing.TypeAlias` if your type alias might be otherwise confused with a global assignment.

### Literals

- You can use `typing.Literal` when you want to restrict based on exact values.
  
```python
from typing_extensions import Literal

PrimaryColors = Literal["red", "yellow", "blue"]
```

- Consider tagging an attribute with the `Literal` type to discriminate between models in a returned Union. This avoids the need to do `isinstance` checks on the return type.

### Final

- If you have a type that should not change or get re-assigned in the code, consider typing it as `typing.Final`.

```python
from typing_extensions import Final

MAX_BLOB_SIZE: Final = 4 * 1024 * 1024
```

- If you have a method that should not be overridden or a class that should not be subclassed, consider decorating with `@final`.

```python
from typing_extensions import final

class BlobClient:
    @final
    def download(self) -> None:
        ...
```


### NewType

- Use `typing.NewType` to restrict a type to a specific context and catch certain programming errors.

```python
from typing import NewType

Sanitized = NewType("Sanitized", str)


def sanitize(log) -> Sanitized:
    return Sanitized(_sanitize(log))

def print_log(log: Sanitized) -> None: ...
```
