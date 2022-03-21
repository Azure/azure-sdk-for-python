# Python SDK Typing and Static Type Checker Guide

This guide walks through the setup necessary to run mypy, a static type checker, on client library code. It also contains some general typing tips and guidance as it relates to common types/patterns we use in the Python SDK.

### Table of contents

- [Intro to typing in Python]()
- [Typing a client library]()
- [Types usable in annotations]()
- [Install and run mypy on your client library code]()
- [Typing tips and guidance for the Python SDK]()    
   - [Debug mypy with reveal_type() and reveal_locals()]()
   - [Use typing.Any sparingly]()
   - [Use typing.Union when accepting more than one type]()
   - [Use typing.Optional when a parameter default is None]()
   - [Typing for collections]()
       - [Mapping types]()
       - [List]() 
       - [Tuple]()
   - [Passing a function or a class as a parameter or return type]()
   - [Typing variadic arguments - *args and **kwargs]()
   - [Use forward references when the type is not defined yet]()
   - [Use typing.overload to overload a function]()
   - [Use typing.cast to help mypy understand a type]()
   - [Use typing.Protocol for structural subtyping]()
   - [Use TypeVar for generic type hinting]()
   - [Use AnyStr when your parameter accepts both str and bytes]()
   - [Use typing.TypeAlias when creating a type alias]()
   - [Use TYPE_CHECKING to avoid circular imports]()
- [How to ignore a mypy typing error]()
- [How to opt out of mypy type checking]()

## Intro to typing in Python

Python is a dynamically typed (or sometimes called "duck typed") language. This means that type checking is done at runtime and types are allowed to change.
This is different from more statically typed languages, like Java, where you will have you declare types in code and check them at compile time.
However, with PEP 484, type hints were introduced to Python which makes it possible to do the static type checking of Python code.
Type hints can be written into Python code to indicate the type of a variable, argument, return type, etc. There are tools available to perform static type checking using type hints, like mypy. Note that type hints have no effect on the code at runtime and are not enforced by the interpreter.

There are some key benefits to using and checking type hints in Python code:
1) type hints checked by a static type checker can help developers find bugs in Python code (type hints can be thought of as "free" unit tests, although they do not replace a thorough test suite).
2) type hints are shipped in our packages so that customers can consume them to further type check their own applications and get improved IDE and Intellisense experiences

There are two styles of type hints: comment and annotation (preferred).

Type comments are Python 2 compatible and consist of comments in the code which indicate the types of arguments and return values.
Note that these are truly just comments in the code which the type checker can use.

```python
from typing import Any, Optional

def download_blob_from_url(
        blob_url,  # type: str
        output,  # type: str
        credential=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
    # type: (...) -> None
    ...
```

Since Python 3, type annotations were introduced and are the **preferred** method of adding type hints to your code. Annotations provide a cleaner syntax and let you keep the type information closer, or inline with the code.

```python
from typing import Any, Optional

def download_blob_from_url(
        blob_url: str,
        output: str,
        credential: Optional[Any] = None,
        **kwargs: Any
    ) -> None:
    ...
```

A fully annotated signature includes type annotations for all parameters and the return type. The type of a parameter should follow 
the `:` syntax and a default argument can be supplied like in the `credential` parameter above. A return type follows the function def with
an arrow, its type, and then `:`.

Note that since Python 3.6, it is also possible to add type annotations to variables. The syntax follows the same as function arguments: 

```python
length: int = 42
width: int = 8
area: int = length * width
```

When typing your library, note that almost anything can be used as a type - built-ins like `str`, `int`, `bool`, types from the `typing` or `typing_extensions` modules, user-defined types, abstract base classes, and more. 
See [Types usable in annotations]() for more information.


## Typing a client library

When starting to add type hints to a client library, there are a few things to consider. 
First, Python has a "gradual type system". What this means is that typing is not an all-or-nothing task - you can gradually add types into your code and any code without type hints will just be ignored by the type checker.
Typing is always optional and this is a good thing! Pushing to achieve full coverage of annotated code can lead to low signal-to-noise and sometimes is not practical or impossible given the expressiveness of Python as a language.
So, in practice, what should you aim to type?

1) Add type hints to publicly exposed APIs in the client library. Type hints get shipped with our client libraries and provide benefit to our users.
To ensure that type hints do get shipped in your library, follow the steps below or use the `template` library when creating a new package.
   a) add an empty `py.typed` file to the base of your package
   b) include the `py.typed` file in the MANIFEST.in
   
2) Add type hints anywhere in the src code where unit tests are worth writing. Consider typing/mypy as "free" tests for your library so focusing typing on
high density/important areas of the code helps in detecting bugs.

### Types usable in annotations

Almost anything can be used as a type in annotations.

1) Basic types like `int`, `str`, `bytes`, `float`, `bool`
2) Classes or abstract base classes - whether user-defined, from the standard library like [collections]() or [collections.abc](), or external packages
3) Types from the [typing]() or [typing_extensions]() modules
4) Built-in generic types, like `list` or `dict`*.
   > *Note: Support for generic types was not added until Python 3.9 as well (or 3.7+ with `from __future__ import annotations` import). For example, this lets you pass in generic `list[str]` as a type hint rather than `typing.List[str]`. 

Here are a few considerations and notes on Python version support:

- With PEP585 and PEP563, importing certain generic collection types from `typing` has been [deprecated](https://peps.python.org/pep-0585/#implementation) in favor for using the types in `collections.abc` or generic type hints (like `list`) from the standard library.
At the time of writing, the Python SDK supports 3.6+ and so we must still import these types from `typing` or check the Python version
at runtime before importing (Note that the `collections.abc` types did not have [] notation added until 3.9)

```python
import sys

if sys.version_info < (3, 9):
  from typing import Sequence
else:
  from collections.abc import Sequence
```

- The `typing-extensions` library backports types that are introduced only in later versions of Python (e.g. `Protocol` which was introduced in Python 3.8) so that they can be used as early as Python 3.6.

```python
from typing_extensions import Protocol
```

Our azure-core library takes a dependency on `typing-extensions` so for most client libraries the dependency is already implicit.
See the [typing-extensions]() docs to check what has been backported.

## Install and run mypy on your client library code

Our Python SDK repo has the version of mypy that we run in CI pinned to a specific version. This is to avoid surprise typing errors raised when a new version of `mypy` ships.
All client libraries in the Python SDK repo are automatically opted in to running mypy (TODO not yet).

The easiest way to install and run mypy locally is with tox. This reproduces the exact mypy environment run in CI and brings in the third party stub packages necessary.

`pip install tox tox-monorepo`

To run mypy on your library, run tox mypy env at the package level:

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics>tox -e mypy -c ../../../eng/tox/tox.ini`

If you don't want to use `tox` you can also install and run `mypy` on its own:

`pip install mypy`
`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics>mypy azure`

Note that you may see different errors if running a different version of `mypy` than the one in CI.

If specific configuration of mypy is needed for your library, use a mypy.ini file at the package level:

`.../azure-sdk-for-python/sdk/textanalytics/azure-ai-textanalytics/mypy.ini`

For example, you might want mypy to ignore type checking files under a specific directory:

```md
[mypy-azure.ai.textanalytics._generated.*]
ignore_errors = True
```

Full documentation on mypy config options found here: TODO


## Typing tips and guidance for the Python SDK

This is not intended to be a complete guide to typing in Python. This section covers some common typing scenarios encountered when working on the SDK and provides some tips.
Typing is relatively new to Python, with over 20 PEPs and counting. Please check the `mypy` and `typing` documentation for the most up-to-date information.

mypy's own common issues page: https://mypy.readthedocs.io/en/stable/common_issues.html


### Debug mypy with reveal_type and reveal_locals

Sometimes `mypy` might raise an error that is difficult to understand -- luckily it is possible to debug mypy and see what it is thinking / what types it is inferring.
`reveal_type(expr)` and `reveal_locals()` are debugging functions recognized by mypy. `reveal_type(expr)` can be placed in code and will tell you the inferred static type of an expression.
`reveal_locals()` can also be placed on any line and will tell you the inferred types of all local variables. 

```python
from typing import Union, List

def print_things(thing: Union[int, List[int]]) -> None:
    if isinstance(thing, int):
        reveal_type(thing)
        print(thing)

    reveal_type(thing)
    print(st for st in thing)
```

Running mypy on the above reveals the types that mypy sees:

> main.py:5: note: Revealed type is "builtins.int"
> main.py:8: note: Revealed type is "Union[builtins.int, builtins.list[builtins.int]]"
> main.py:9: error: Item "int" of "Union[int, List[int]]" has no attribute "__iter__" (not iterable)
> Found 1 error in 1 file (checked 1 source file)

These debugging functions don't need to be imported from anywhere and are only recognized by mypy - therefore you will need to remove them from code before runtime.


### Use typing.Any sparingly

`typing.Any`, like the name suggests, assumes that a type can be _anything_ - it is compatible with every other type, and vice versa. This is what allows gradual typing in Python, as an untyped function like this...

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
something more specific, that is preferred since over usage of `Any` can undermine the type checker's ability to find bugs in other parts of the code.


### Use typing.Union when accepting more than one type

[typing.Union](https://docs.python.org/3/library/typing.html#typing.Union) allows for typing an argument with more than one type.

```python
from typing import Union

def foo(bat: Union[float, str]) -> None:
   ...
```

Tips:
A `Union` requires at least two types and is more useful with types that are not consistent with each other. For example,
usage of `Union[int, float]` is not necessary since `int` is consistent with `float` -- just use `float`. It's also recommended trying to
avoid having functions return `Union` types as it causes the user to need to understand/parse through the return value before acting on it.
Sometimes this can be resolved by using an [overload]().


### Use typing.Optional when a parameter default is None

Python's typing docs for Optional explain that 

> Optional[X] is equivalent to X | None (or Union[X, None])

This means that Optional should only be used when an argument can be either something _or_ None. For example, Optional usage is appropriate here:

```python
from typing import Optional

def tree(kind: Optional[str] = None):
    ...
```

But not necessary here...

```python
def tree(kind: str = "oak"):
    ...
```

> Note: The `X | None` syntax is only supported in Python 3.10+

### Typing for collections

There are a few things to consider when typing collections in Python.

1) "Be conservative in what you send, be liberal in what you accept." - The Robustness Principle 
In other words, we should try to be specific in what we say we return - it's more helpful to specify concrete types which a user can reason about easily than abstract types.
We should also aim to be lenient in the types we accept as a parameter because this allows for more flexibility for the caller, 
e.g. accepting an `Iterable` where appropriate allows for more possible types to passed (list, tuple, dict, etc.) than specifying a `List`.

2) It can be more useful to consider the set of supported operations as the defining characteristic of a type.
   Prefer structural subtyping over nominal typing as this is what supports duck typing in Python.

#### Mapping Types

Syntax for mapping types follows: MappingType[KeyType, ValueType].
For example, typing.Dict[str, str] says that the type is a dictionary with string keys and string values.

For parameter types, consider using `typing.Mapping` or `typing.MutableMapping`. If the function accepting the mapping type does
not need to mutate the mapping, `typing.Mapping` provides more flexibility than `typing.MutableMapping` (which implements methods
like `pop`, `update`, `clear`).

For example, 

```python
from typing import Mapping

def create_table(entity: Mapping[str, str]) -> None:
    ...
```

By accepting `typing.Mapping` here, we give more flexibility to the user and allow them to specify anything consistent 
with a `typing.Mapping` - dict, defaultdict, a user-defined dict-like class, or a subtype of `typing.Mapping`. 
Had we specified a generic `typing.Dict` here, the `entity` passed must be a `dict` or one of its subtypes, narrowing 
the types accepted.

#### List

The [typing.List](https://docs.python.org/3/library/typing.html#typing.List) docs make a recommendation:

> Useful for annotating return types. To annotate arguments it is preferred to use an abstract collection type such as Sequence or Iterable

For iterable parameter types, consider using `typing.Sequence` or `typing.MutableSequence` or even plain `Iterable` depending on what needs the function
has for the collection type.

In determining whether to use, for example, `Sequence` or `Iterable` as a parameter type, it's important to understand the supported operations of each and
how much flexibility we can give the caller. A good reference for the set of supported operations for generic collections 
is found here: https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes
For example, `Iterable` input is flexible in that it can accept a generator as input, whereas `Sequence` is not -- it must provide the ability to call `len()`.

#### Tuples

Special mention for `Tuple` since there are a few ways to type annotate with a tuple.
`typing.Tuple` syntax follows:

`Tuple[str, int, float]` for a tuple defined for item, quantity, price:

item = ("pencil", 1, 0.99)

If the tuple has an arbitrary amount of same type arguments, you can use `...` syntax:

Tuple[str, ...]

`typing.NamedTuple` can also be used as a factory for tuple subclasses:

```python
from typing import NamedTuple

class Point(NamedTuple):
  x: float
  y: float

def bounding_box(points: List[Point]) -> None: ...
```

Note that `Point` is consistent with Tuple[float, float], but not vice versa. In other words, you can't pass a vanilla
Tuple[float, float] into the `bounding_box` function above, but if it were annotated as `points: Tuple[float, float]`, a `Point`
would be permissible.

### Passing a function or a class as a parameter or return type

`typing.Callable` can be used to annotate callback parameters or functions returned by higher-order functions.
Syntax as follows:

Callable[[ParamType1, ParamType2, ...], ReturnType]

The argument list must be a list of types (or ...) and a single type for the return type.

```python
from typing import Callable

def add(x: int, y: int) -> int:
  return x + y

def multiply(x: int, y: int) -> int:
  return x * y

def do_math(op: Callable[[int, int], int], x: int, y: int) -> int:
  return op(x, y)
```

To type annotate a class, it depends on if the class has already been initialized or not.

In the below example, `make_quack` accepts an initialized `Duck` while `create_duck` accepts a class object of `Duck`.
The former can be written as `Duck` while the latter should be written as `typing.Type[Duck]` to indicate this difference.

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

Running mypy shows the expected (and unexpected) output:
 
main.py:15: error: Argument 1 to "create_duck" has incompatible type "Duck"; expected "Type[Duck]"
main.py:17: error: Argument 1 to "make_quack" has incompatible type "Type[Duck]"; expected "Duck"
Found 2 errors in 1 file (checked 1 source file)


### Use typing.TypeAlias when creating a type alias

With PEP 613, `typing.TypeAlias` was introduced to make type aliases more obvious to the type checker.

```python
# from typing import TypeAlias Python >=3.10
from typing_extensions import TypeAlias

CredentialTypes: TypeAlias = Union[AzureKeyCredential, TokenCredential]

```

This removes ambiguity for the type checker and indicates this isn't a normal variable assignment.

> Note that TypeAlias is backported to older versions of Python by using typing_extensions


### Typing variadic arguments - *args and **kwargs

Many of our client methods take a `**kwargs` and sometimes an `*args` argument.

Consider the below example:

```python
def begin_operation(*args, **kwargs) -> None:
    ...
```

Here, let's assume that *args accepts an arbitrary number of positional parameters which must be of type `str`. 
Let's also assume that **kwargs accepts operation-specific keyword arguments, including any azure-core specific 
keyword arguments. In this case, we can narrow the type for *args to `str`. For **kwargs, due to the complexity 
of the type, we will leave it as `Any`. Typed this looks like:

```python
from typing import Any

def begin_operation(*args: str, **kwargs: Any) -> None:
    ...
```

Note how mypy understands these types:

```python
from typing import Any

def begin_operation(*args: str, **kwargs: Any) -> None:
    reveal_locals()
```

main.py:4: note: Revealed local types are:
main.py:4: note:     args: builtins.tuple[builtins.str]
main.py:4: note:     kwargs: builtins.dict[builtins.str, Any]]"

Mypy correctly infers *args as a tuple[str] and **kwargs as a dict[str, Any] so we do not need to type these as such in the code.
If *args accepts more than just `str`, a Union[] type or `Any` can be used depending on how complex the type is.

### Use AnyStr when your parameter accepts both str and bytes

The `typing` module includes a pre-defined `TypeVar` named `AnyStr`. Its definition looks like this:

```python
from typing import TypeVar

AnyStr = TypeVar('AnyStr', bytes, str)
```

`AnyStr` can be used in many functions that accept either bytes or str, and return values of the given type.

> Note: The `TypeVar` is a generic type which restricts `AnyStr` to `bytes` or `str`. More information on [TypeVar]()

### cast

Sometimes `mypy` will be unable to infer a type and may raise a false positive error. Using `typing.cast` is a way to tell `mypy` what
the type of something is and is generally favored over using a `# type: ignore` comment.

The below snippet shows an example of how mypy might need a little help to understand the parameter type specified in a union:

```python
from typing import Union, List, Optional, Any, cast

def receive_deferred_messages(
    self, sequence_numbers: Union[int, List[int]], *, timeout: Optional[float] = None, **kwargs: Any
) -> List[ServiceBusReceivedMessage]:

    if isinstance(sequence_numbers, int):
        sequence_numbers = [sequence_numbers]
    sequence_numbers = cast(List[int], sequence_numbers)  # mypy clarity
```

If you are using cast often, however, it might be an indication that the code should be otherwise written or refactored.
Note that mypy casts are only used by the type checker and do not perform a runtime type check.

### Use forward references when the type is not defined yet

This is commonly encountered when using `@classmethod`. Because the type does not exist yet, when trying to use it in a type hint, python complains at runtime.

```python
class TreeHouse:
    def __init__(self): ...

    @classmethod
    def build(cls) -> TreeHouse:
        return cls()
```

```text
    class TreeHouse:
  File "testing_mypy.py", line 12, in TreeHouse
    def build(cls) -> TreeHouse:
NameError: name 'TreeHouse' is not defined
```

A forward reference can be used to fix the runtime issue. Simply place the type in quotations like "TreeHouse":

```python
class TreeHouse:
    def __init__(self) -> None: ...

    @classmethod
    def build(cls) -> "TreeHouse":
        return cls()
```

`mypy` recognizes this syntax and will understand the type as `TreeHouse`. 

Another situation where forward references can be useful is when a type hint is used before a type is defined in a file.

```python
class Yurt:
  def add(house: "TreeHouse") -> None: ...

class TreeHouse:
    def __init__(self) -> None: ...
```


> Note: While this issue is easily resolved by adding `from __future__ import annotations`, this is currently only supported in Python 3.7+.


### Use TYPE_CHECKING to avoid circular imports

`typing.TYPE_CHECKING` is a constant that is evaluates to `True` when mypy is running, but is otherwise `False` at runtime.
A common instance of when you might need to use TYPE_CHECKING is when a circular import is created due to imports necessary for type annotations:

a.py
```python
from b import Baz

def foo(b: Baz) -> None:
  b.hello()

def bar() -> None:
    print("bar")
```

b.py

```python
from a import bar

class Baz:
  def hello(self) -> None: ...

```

Here `a` imports from `b` and `b` imports from `a`, causing a circular import at runtime:

`ImportError: cannot import name 'Baz' from partially initialized module 'b' (most likely due to a circular import)`

Since TYPE_CHECKING is only `True` when running the type checker, we can add our imports under a TYPE_CHECKING block to fix this issue in a.py:

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

Note that we also had to change Baz to a forward reference since it will not be defined at runtime under the TYPE_CHECKING conditional.

### Use TypeVar for generic type hinting

`TypeVar` is a generic type which can be bound to a specific type with each usage. Common usage might be to have the parameter
type reflected on the result type:

```python
from typing import Sequence, TypeVar

T = TypeVar("T")

def pick(p: Sequence[T]) -> T:
  return random_pick(p)
```

This leaves the type open for the caller to pass a Sequence[int], Sequence[float], Sequence[str], etc. and promises to return the same type passed in.

You can restrict a `TypeVar` to several specific types by adding the types as positional arguments:

```python
from typing import Sequence, TypeVar

T = TypeVar("T", int, str)

def pick(p: Sequence[T]) -> T:
  return random_pick(p)
```

There are also arguments available to set the upper boundary or variance in a `TypeVar` -- please see the [reference docs](https://docs.python.org/3/library/typing.html#typing.TypeVar) for more information.

### Use typing.Protocol for structural subtyping

PEP 544 introduced the `Protocol` type. The `Protocol` type helps Python support _structural subtyping_ or "static duck typing".
In other words, when looking at whether two types are compatible, the actual structure and capabilities are more important than the name of type.

A `Protocol` type can be defined by one or more methods, and a type checker will verify that those methods are implemented where a protocol type is specified.

Below we create a `SupportsFly` protocol class which expects a `fly()` method on compatible types being passed into `ascend()`:

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

p = Penguin()
ascend(p)  # Mypy complains below
```

Running mypy shows expected output:

`main.py:23: error: Argument 1 to "ascend" has incompatible type "Penguin"; expected "SupportsFly"
Found 1 error in 1 file (checked 1 source file)`

Any type that is consistent with, or implements all the methods defined by the SupportsFly protocol, is acceptable to pass into ascend().
A difference between Protocols and abstract classes - Protocols work at typing time while abc work at runtime.
A class does not need to _inherit_ from Protocol like an abc, the type checker will simply enforce its usage at typing time.

A common Python SDK Protocol type we use is [azure.core.credentials.TokenCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/credentials.py).
TokenCredential requires that a type implements the `get_token` method for it to be consistent with the Protocol.

See more on Protocols in the [reference documentation](https://docs.python.org/3/library/typing.html#typing.Protocol).

### Use typing.overload to overload a function

`typing.overload` allows for annotating different combinations of arguments for a function. This is useful when the return type
might depend on the type or types of parameters.

Consider a function which takes in different input types which then inform the output type:

```python
from typing import Union

def analyze_text(text: str, analysis_kind: Union[SentimentAnalysis, EntityRecognition, LanguageDetection]) -> Union[SentimentResult, EntityRecognitionResult, LanguageDetectionResult]:
    return _analyze(text, analysis_kind)
```

We can annotate this function with overloads to help inform the type checker (and intellisense) which input maps to which output type.

```python
from typing import overload

@overload
def analyze_text(text: str, analysis_kind: LanguageDetection) -> LanguageDetectionResult:
    ...

@overload
def analyze_text(text: str, analysis_kind: EntityRecognition) -> EntityRecognitionResult:
    ...

@overload
def analyze_text(text: str, analysis_kind: SentimentAnalysis) -> SentimentResult:
    ...

def analyze_text(text, analysis_kind):  # the actual implementation doesn't need to be annotated
    return _analyze(text, analysis_kind)
```

Running mypy shows that the correct return type is inferred from the input type:

```python
result = analyze_text("my text", LanguageDetection())
reveal_type(result)
```

`main.py:28: note: Revealed type is "__main__.LanguageDetectionResult"`

Another use of typing.overload is when there are a different number of arguments. We can take the above example and imagine that
`analyze_text` has an additional overload which does not take an `analysis_kind`:

```python
from typing import overload

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

def analyze_text(*args, **kwargs):  # the actual implementation doesn't need to be annotated
    # logic parsing args / kwargs
    ...
```

Running mypy again shows that it understands the return types based on the difference in arguments:

```python
language_result = analyze_text("my text", LanguageDetection())
reveal_type(language_result)

text_result = analyze_text("my text")
reveal_type(text_result)
```

`main.py:36: note: Revealed type is "__main__.LanguageDetectionResult"`
`main.py:39: note: Revealed type is "builtins.str"`


## How to ignore mypy errors

A mypy error can be ignored by placing a `# type: ignore` comment on the offending line. Generally, we do not want to 
ignore mypy errors if we can, but sometimes it is not possible to fix the error, e.g. there might be bug in mypy or 
python as a language is just acting more expressive than the type system allows.
If you must ignore a mypy error, it is recommended that you explain your reasoning in the ignore comment / include a 
link to the bug or issue so someone reading the code later may resolve it.

Note that it is possible to be specific in the mypy error to ignore, instead of globally turning off type checking on 
that line. Syntax for this involves putting the specific mypy error code in brackets of the ignore comment:

```python
ignore_me: int = 5  # type: ignore[misc]
```

To find the error code associated with your mypy error, run mypy with command argument `--show-error-codes`.

More information about ignoring mypy errors can be found in the official [mypy docs](https://mypy.readthedocs.io/en/stable/type_inference_and_annotations.html?highlight=ignore#silencing-type-errors).


## How to opt out of mypy type checking

All client libraries in the Python SDK repo are automatically opted in to running mypy (TODO not yet). If there is a 
reason why a particular library should not run mypy, it is possible to add that library to a block list to prevent
mypy from running checks.

1) Place the package name on this block list: <url>
2) Open an issue tracking that <library-name> should be opted in to running mypy
