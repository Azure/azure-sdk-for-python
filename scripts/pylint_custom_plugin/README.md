## Linting the Guidelines

In order to lint for the guidelines, you must make sure you are using the pylintrc file.
It is recommended you run pylint at the library package level to be consistent with how the CI runs pylint.

Check that you are running pylint version >=2.5.2 and astroid version >=2.4.1.

**How to run pylint locally using the pylintrc:**

1. Run pylint at the root of the repo and it will automatically find the pylintrc:
    ```bash
    C:\azure-sdk-for-python>pylint sdk/storage/azure-storage-blob/azure
    ```
2. Add the --rcfile command line argument with a relative path to the pylintrc from your current directory:
    ```bash
    C:\azure-sdk-for-python\sdk\storage>pylint --rcfile="../../pylintrc" azure-storage-blob
    ```
3. Set the environment variable PYLINTRC to the absolute path of the pylintrc file:
    ```bash
    set PYLINTRC=C:\azure-sdk-for-python\pylintrc
    ```
    Run pylint:
    ```bash
    C:\azure-sdk-for-python\sdk\storage>pylint azure-storage-blob
    ```
4. Run pylint at the package level using tox and it will find the pylintrc file:
    ```bash
    C:\azure-sdk-for-python\sdk\storage\azure-storage-blob>tox -c ../../../eng/tox/tox.ini -e lint
    ```
5. If you use the pylint extension for VS code or Pycharm it *should* find the pylintrc automatically.

**How to disable a pylint error:**
```bash
# pylint:disable=connection-string-should-not-be-constructor-param
```

The pylint custom checkers for SDK guidelines fall into messages range C4717 - C4738.
You will know you came across a custom checker if it contains a link to the guidelines.

In the case of a false positive, use the disable command to remove the pylint error.

**Guidelines that are currently linted:**

| Pylint checker name                                | How to fix this                                                                                                                                                      | How to disable this rule                                                                 | Link to python guideline                                                                      |
|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| client-method-should-not-use-static-method         | Use module level functions instead.                                                                                                                                  | # pylint:disable=connection-string-should-not-be-constructor-param                       | [link](https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods) |
| missing-client-constructor-parameter-credential    | Add a credential parameter to the client constructor. Do not use plural form "credentials".                                                                          | # pylint:disable=missing-client-constructor-parameter-credential                         | [link](https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods) |
| missing-client-constructor-parameter-kwargs        | Add a **kwargs parameter to the client constructor.                                                                                                                  | # pylint:disable=missing-client-constructor-parameter-kwargs                             | [link](https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods) |
| client-method-has-more-than-5-positional-arguments | Use keyword arguments to reduce number of positional arguments.                                                                                                      | # pylint:disable=client-method-has-more-than-5-positional-arguments                      | [link]((https://azure.github.io/azure-sdk/python_design.html#method-signatures)          |
| client-method-missing-type-annotations             | Check that param/return type comments are present or that param/return type annotations are present. Check that you did not mix type comments with type annotations. | # pylint:disable=client-method-missing-type-annotations                                  | [link]((https://azure.github.io/azure-sdk/python_design.html#types-or-not)               |
| client-incorrect-naming-convention                 | Check that you use... snake_case for variable, function, and method names. Pascal case for types. ALL CAPS for constants.                                            | # pylint:disable=client-incorrect-naming-convention                                      | [link]((https://azure.github.io/azure-sdk/python_design.html#naming-conventions)         |
| client-method-missing-kwargs                       | Check that any methods that make network calls have a **kwargs parameter.                                                                                            | # pylint:disable=client-method-missing-kwargs                                            | [link](https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods) |
| config-missing-kwargs-in-policy                    | Check that the policies in your configuration function contain a **kwargs parameter.                                                                                 | # pylint:disable=config-missing-kwargs-in-policy                                         | [link](https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods) |
| async-client-bad-name                              | Remove "Async" from your service client's name.                                                                                                                      | # pylint:disable=async-client-bad-name                                                   | [link](https://azure.github.io/azure-sdk/python_design.html#async-support)                    |
| file-needs-copyright-header                        | Add a copyright header to the top of your file.                                                                                                                      | # pylint:disable=file-needs-copyright-header                                             | [link](https://azure.github.io/azure-sdk/policies_opensource.html)                            |
| client-method-name-no-double-underscore            | Don't use method names prefixed with "__".                                                                                                                           | # pylint:disable=client-method-name-no-double-underscore                                 | [link]((https://azure.github.io/azure-sdk/python_design.html#public-vs-private)          |
| specify-parameter-names-in-call                    | Specify the parameter names when calling methods with more than 2 required positional parameters. e.g. self.get_foo(one, two, three=three, four=four, five=five)     | # pylint:disable=specify-parameter-names-in-call                                         | [link]((https://azure.github.io/azure-sdk/python_design.html#method-signatures)          |
| connection-string-should-not-be-constructor-param  | Remove connection string parameter from client constructor. Create a method that creates the client using a connection string.                                       | # pylint:disable=connection-string-should-not-be-constructor-param                       | [link](https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods) |
| package-name-incorrect                             | Change your distribution package name to only include dashes, e.g. azure-storage-file-share                                                                          | # pylint:disable=package-name-incorrect                                                  | [link](https://azure.github.io/azure-sdk/python_implementation.html#packaging)                |
| client-suffix-needed                               | Service client types should use a "Client" suffix, e.g. BlobClient.                                                                                                  | # pylint:disable=client-suffix-needed                                                    | [link](https://azure.github.io/azure-sdk/python_design.html#clients)                          |
| docstring-admonition-needs-newline                 | Add a blank newline above the .. literalinclude statement.                                                                                                           | # pylint:disable=docstring-admonition-needs-newline                                      | No guideline, just helps our docs get built correctly for microsoft docs.                     |