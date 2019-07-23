# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Pylint custom checkers for SDK guidelines: CXXXX - CXXXX
"""
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker


class ClientConstructorTakesCorrectParameters(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-constructor"
    priority = -1
    msgs = {
        "C4717": (
            "Client constructor is missing a credentials parameter. See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-constructorsfactory-methods",
            "missing-client-constructor-parameter-credentials",
            "All client types should accept a credentials parameter.",
        ),
        "C4719": (
            "Client constructor is missing a **kwargs parameter. See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-constructorsfactory-methods",
            "missing-client-constructor-parameter-kwargs",
            "All client types should accept a **kwargs parameter.",
        )
    }
    options = (
        (
            "ignore-missing-client-constructor-parameter-credentials",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client constructors without a credentials parameter",
            },
        ),
        (
            "ignore-missing-client-constructor-parameter-kwargs",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client constructors without a **kwargs parameter",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        if node.name.endswith("Client"):
            self.is_client.append(True)
        else:
            self.is_client.append(False)

    def visit_functiondef(self, node):
        if node.name == "__init__" and self.is_client and self.is_client[-1]:
            arguments_node = next(
                (child for child in node.get_children() if child.is_argument)
            )
            arg_names = [argument.name for argument in arguments_node.args]
            if "credential" not in arg_names and "credentials" not in arg_names:
                self.add_message(
                    msg_id="missing-client-constructor-parameter-credentials", node=node, confidence=None
                )
            if not arguments_node.kwarg:
                self.add_message(
                    msg_id="missing-client-constructor-parameter-kwargs", node=node, confidence=None
                )


class ClientHasKwargsInPoliciesForCreateConfigurationMethod(BaseChecker):
    __implements__ = IAstroidChecker

    name = "configuration-policies-kwargs"
    priority = -1
    msgs = {
        "C4714": (
            "A policy in the create_configuration() function is missing a **kwargs argument. See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-constructorsfactory-methods",
            "config-missing-kwargs-in-policy",
            "All policies should take a **kwargs parameter.",
        )
    }
    options = (
        (
            "ignore-config-missing-kwargs-in-policy",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow clients instantiate a policy without a kwargs parameter.",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_functiondef(self, node):
        if node.name == "create_configuration" or node.name == "create_config":
            node.decorators = None
            for idx in range(len(node.body)):
                line = list(node.get_children())[idx].as_string()
                if line.find("Policy") != -1:
                    if line.find("**kwargs") == -1:
                        self.add_message(
                            msg_id="config-missing-kwargs-in-policy",
                            node=list(node.get_children())[idx],
                            confidence=None
                        )


class ClientHasApprovedMethodNamePrefix(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-approved-method-name-prefix"
    priority = -1
    msgs = {
        "C4715": (
            "Client is not using an approved method name prefix. See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-constructorsfactory-methods",
            "unapproved-client-method-name-prefix",
            "All clients should use the preferred verbs for method names.",
        )
    }
    options = (
        (
            "ignore-unapproved-client-method-name-prefix",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow clients to not use preferred method name prefixes",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        if node.name.endswith("Client"):
            client_methods = [child for child in node.get_children() if child.is_function]

            approved_prefixes = ["get", "list", "create", "upsert", "set", "update", "replace", "append", "add",
                                 "delete", "remove", "begin"]
            for idx, method in enumerate(client_methods):
                if method.name.startswith("__") or "_exists" in method.name or method.name.startswith("_") \
                        or method.name.startswith("from"):
                    continue
                prefix = method.name.split("_")[0]
                if prefix.lower() not in approved_prefixes:
                    self.add_message(
                        msg_id="unapproved-client-method-name-prefix",
                        node=client_methods[idx],
                        confidence=None
                    )


class ClientMethodsUseKwargsWithMultipleParameters(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-method-multiple-parameters"
    priority = -1
    msgs = {
        "C4720": (
            "Client has too many positional arguments. Use keyword-only arguments."
            " See details: https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-method-signatures",
            "client-method-has-more-than-5-positional-arguments",
            "Client method should use keyword-only arguments for some parameters.",
        )
    }
    options = (
        (
            "ignore-client-method-has-more-than-5-positional-arguments",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client method to have more than 5 positional arguments",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        if node.name.endswith("Client"):
            self.is_client.append(True)
        else:
            self.is_client.append(False)

    def visit_functiondef(self, node):
        if self.is_client and self.is_client[-1]:
            try:
                arguments_node = next(
                    (child for child in node.get_children() if child.is_argument)
                )

                # Only bother checking method signatures with > 6 parameters (don't include self/cls/etc)
                if len(arguments_node.args) > 6:
                    positional_args = len(arguments_node.args) - len(arguments_node.defaults)
                    if positional_args > 6:
                        self.add_message(
                            msg_id="client-method-has-more-than-5-positional-arguments", node=node, confidence=None
                        )
            except AttributeError:
                pass

    def visit_asyncfunctiondef(self, node):
        if self.is_client and self.is_client[-1]:
            try:
                arguments_node = next(
                    (child for child in node.get_children() if child.is_argument)
                )

                # Only bother checking method signatures with > 6 parameters (don't include self/cls/etc)
                if len(arguments_node.args) > 6:
                    positional_args = len(arguments_node.args) - len(arguments_node.defaults)
                    if positional_args > 6:
                        self.add_message(
                            msg_id="client-method-has-more-than-5-positional-arguments", node=node, confidence=None
                        )
            except AttributeError:
                pass


class ClientMethodsHaveTypeAnnotations(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-method-type-annotations"
    priority = -1
    msgs = {
        "C4721": (
            "Client method is missing type annotations and/or return type annotations. See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#python-type-hints",
            "client-method-missing-type-annotations",
            "Client method should use type annotations.",
        )
    }
    options = (
        (
            "ignore-client-method-missing-type-annotations",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client method without type annotations",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        if node.name.endswith("Client"):
            self.is_client.append(True)
        else:
            self.is_client.append(False)

    def visit_functiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if not node.name.startswith("_") or node.name == "__init__":
                try:
                    arguments_node = next(
                        (child for child in node.get_children() if child.is_argument)
                    )

                    # Checks that method has python 2/3 type comments or annotations as shown here:
                    # https://www.python.org/dev/peps/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code

                    # check for type comments
                    if node.type_comment_args is None or node.type_comment_returns is None:

                        # type annotations default to None when not present, so need extra logic here
                        type_annotations = [type_hint for type_hint in arguments_node.annotations if type_hint is not None]

                        # check for type annotations
                        if (type_annotations == [] and len(arguments_node.args) > 1) or node.returns is None:
                            self.add_message(
                                msg_id="client-method-missing-type-annotations", node=node, confidence=None
                            )
                except AttributeError:
                    pass

    def visit_asyncfunctiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if not node.name.startswith("_") or node.name == "__init__":
                try:
                    arguments_node = next(
                        (child for child in node.get_children() if child.is_argument)
                    )

                    # Checks that method has python 2/3 type comments or annotations as shown here:
                    # https://www.python.org/dev/peps/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code

                    # check for type comments
                    if node.type_comment_args is None or node.type_comment_returns is None:

                        # type annotations default to None when not present, so need extra logic here
                        type_annotations = \
                            [type_hint for type_hint in arguments_node.annotations if type_hint is not None]

                        # check for type annotations
                        if (type_annotations == [] and len(arguments_node.args) > 1) or node.returns is None:
                            self.add_message(
                                msg_id="client-method-missing-type-annotations", node=node, confidence=None
                            )
                except AttributeError:
                    pass


class ClientMethodsHaveTracingDecorators(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-method-has-tracing-decorator"
    priority = -1
    msgs = {
        "C4722": (
            "Client method is missing the distributed tracing decorator - `distributed_trace`. See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-distributed-tracing",
            "client-method-missing-tracing-decorator",
            "Client method should support distributed tracing.",
        ),
        "C4723": (
            "Client async method is missing the distributed tracing decorator - `distributed_trace_async`. "
            " See details: https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-distributed-tracing",
            "client-method-missing-tracing-decorator-async",
            "Client method should support distributed tracing.",
        ),
    }
    options = (
        (
            "ignore-client-method-missing-tracing-decorator",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client method without tracing decorator.",
            },
        ),
        (
            "ignore-client-method-missing-tracing-decorator-async",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client method without tracing decorator.",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        if node.name.endswith("Client"):
            self.is_client.append(True)
        else:
            self.is_client.append(False)

    def visit_functiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if not node.name.startswith("_"):
                if node.decorators is not None:
                    decorator_present = False
                    for idx in range(len(node.decorators.nodes)):
                        name = list(node.decorators.get_children())[idx].as_string()
                        if name == "distributed_trace":
                            decorator_present = True
                if node.decorators is None or decorator_present is False:
                    self.add_message(
                        msg_id="client-method-missing-tracing-decorator", node=node, confidence=None
                    )

    def visit_asyncfunctiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if not node.name.startswith("_"):
                if node.decorators is not None:
                    decorator_present = False
                    for idx in range(len(node.decorators.nodes)):
                        name = list(node.decorators.get_children())[idx].as_string()
                        if name == "distributed_trace_async":
                            decorator_present = True
                if node.decorators is None or decorator_present is False:
                    self.add_message(
                        msg_id="client-method-missing-tracing-decorator-async", node=node, confidence=None
                    )


class ClientsDoNotUseStaticMethods(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-does-not-use-static-methods"
    priority = -1
    msgs = {
        "C4724": (
            "Client should not use static methods (staticmethod). See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-method-signatures",
            "client-method-should-not-use-static-method",
            "Client method should not use staticmethod.",
        ),
    }
    options = (
        (
            "ignore-client-method-should-not-use-static-method",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client method to use staticmethod.",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        if node.name.endswith("Client"):
            self.is_client.append(True)
        else:
            self.is_client.append(False)

    def visit_functiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if not node.name.startswith("_") and node.decorators is not None:
                for idx in range(len(node.decorators.nodes)):
                    name = list(node.decorators.get_children())[idx].as_string()
                    if name == "staticmethod":
                        self.add_message(
                            msg_id="client-method-should-not-use-static-method", node=node, confidence=None
                        )

    def visit_asyncfunctiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if not node.name.startswith("_") and node.decorators is not None:
                for idx in range(len(node.decorators.nodes)):
                    name = list(node.decorators.get_children())[idx].as_string()
                    if name == "staticmethod":
                        self.add_message(
                            msg_id="client-method-should-not-use-static-method", node=node, confidence=None
                        )


# class FileHasCopyrightHeader(BaseChecker):
#     __implements__ = IAstroidChecker
#
#     name = "file-has-copyright-header"
#     priority = -1
#     msgs = {
#         "C4724": (
#             "File is missing a copyright header. See details:"
#             " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#github-source-headers",
#             "file-needs-copyright-header",
#             "Every source file should have a copyright header.",
#         ),
#     }
#     options = (
#         (
#             "ignore-file-needs-copyright-header",
#             {
#                 "default": False,
#                 "type": "yn",
#                 "metavar": "<y_or_n>",
#                 "help": "Allow file without a copyright header.",
#             },
#         ),
#     )
#
#     import ast
#     ast = ast.parse()
#     print(ast)

class ClientUsesCorrectNamingConventions(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-naming-conventions"
    priority = -1
    msgs = {
        "C4726": (
            "Client is using an incorrect naming convention. See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#python-naming-convention",
            "client-incorrect-naming-convention",
            "Client method should use correct naming conventions.",
        )
    }
    options = (
        (
            "ignore-client-incorrect-naming-convention",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client to use incorrect naming conventions.",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        if "_" in node.name or node.name.endswith("client") or node.name[0] != node.name[0].upper():
            if not node.name.startswith("_"):
                self.add_message(
                    msg_id="client-incorrect-naming-convention", node=node, confidence=None
                )
        else:
            self.is_client.append(True)

        # check for correct naming convention in any class constants
        if node.name.endswith("Client"):
            for idx in range(len(node.body)):
                try:
                    const_name = node.body[idx].targets[0].name
                    if const_name != const_name.upper():
                        self.add_message(
                            msg_id="client-incorrect-naming-convention", node=node.body[idx], confidence=None
                        )
                except AttributeError:
                    pass

    def visit_functiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if node.name != node.name.lower():
                self.add_message(
                    msg_id="client-incorrect-naming-convention", node=node, confidence=None
                )

    def visit_asyncfunctiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if node.name != node.name.lower():
                self.add_message(
                    msg_id="client-incorrect-naming-convention", node=node, confidence=None
                )


class ClientMethodsHaveKwargsParameter(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-constructor"
    priority = -1
    msgs = {
        "C4727": (
            "Client method is missing a **kwargs parameter. See details:"
            " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-constructorsfactory-methods",
            "client-method-missing-kwargs",
            "All client methods should accept a kwargs parameter.",
        ),
    }
    options = (
        (
            "ignore-client-method-missing-kwargs",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client method without a kwargs parameter",
            },
        ),
    )

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        if node.name.endswith("Client"):
            self.is_client.append(True)
        else:
            self.is_client.append(False)

    def visit_functiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if not node.name.startswith("_"):
                try:
                    arguments_node = next(
                        (child for child in node.get_children() if child.is_argument)
                    )
                    if not arguments_node.kwarg:
                        self.add_message(
                            msg_id="client-method-missing-kwargs", node=node, confidence=None
                        )
                except AttributeError:
                    pass

    def visit_asyncfunctiondef(self, node):
        if self.is_client and self.is_client[-1]:
            if not node.name.startswith("_"):
                try:
                    arguments_node = next(
                        (child for child in node.get_children() if child.is_argument)
                    )
                    if not arguments_node.kwarg:
                        self.add_message(
                            msg_id="client-method-missing-kwargs", node=node, confidence=None
                        )
                except AttributeError:
                    pass


def register(linter):
    linter.register_checker(ClientMethodsHaveTracingDecorators(linter))
    linter.register_checker(ClientsDoNotUseStaticMethods(linter))
    linter.register_checker(ClientHasApprovedMethodNamePrefix(linter))
    linter.register_checker(ClientConstructorTakesCorrectParameters(linter))
    linter.register_checker(ClientMethodsUseKwargsWithMultipleParameters(linter))
    linter.register_checker(ClientMethodsHaveTypeAnnotations(linter))
    linter.register_checker(ClientUsesCorrectNamingConventions(linter))
    linter.register_checker(ClientMethodsHaveKwargsParameter(linter))
    linter.register_checker(ClientHasKwargsInPoliciesForCreateConfigurationMethod(linter))
    # linter.register_checker(FileHasCopyrightHeader(linter))