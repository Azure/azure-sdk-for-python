# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Pylint custom checkers for SDK guidelines: C4717 - C4744
"""

import logging
import astroid
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
logger = logging.getLogger(__name__)


class ClientConstructorTakesCorrectParameters(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-constructor"
    priority = -1
    msgs = {
        "C4717": (
            "Client constructor is missing a credential parameter. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#client-configuration",
            "missing-client-constructor-parameter-credential",
            "All client types should accept a credential parameter.",
        ),
        "C4718": (
            "Client constructor is missing a **kwargs parameter. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#client-configuration",
            "missing-client-constructor-parameter-kwargs",
            "All client types should accept a **kwargs parameter.",
        )
    }
    options = (
        (
            "ignore-missing-client-constructor-parameter-credential",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client constructors without a credential parameter",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientConstructorTakesCorrectParameters, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits the constructor within a client class and checks that it has
        credential and kwargs parameters.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.name == "__init__" and node.parent.name.endswith("Client") and \
                    node.parent.name not in self.ignore_clients:
                arg_names = [argument.name for argument in node.args.args]
                if "credential" not in arg_names:
                    self.add_message(
                        msgid="missing-client-constructor-parameter-credential", node=node, confidence=None
                    )
                if not node.args.kwarg:
                    self.add_message(
                        msgid="missing-client-constructor-parameter-kwargs", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if constructor has correct parameters.")
            pass


class ClientHasKwargsInPoliciesForCreateConfigurationMethod(BaseChecker):
    __implements__ = IAstroidChecker

    name = "configuration-policies-kwargs"
    priority = -1
    msgs = {
        "C4719": (
            "A policy in the create_configuration() function is missing a **kwargs argument. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#client-configuration",
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
        super(ClientHasKwargsInPoliciesForCreateConfigurationMethod, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits the any method called `create_configuration` or `create_config` and checks
        that every policy in the method contains a kwargs parameter.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.name == "create_configuration" or node.name == "create_config":
                node.decorators = None
                for idx in range(len(node.body)):
                    # Gets each line of the method as a string
                    line = list(node.get_children())[idx].as_string()
                    if line.find("Policy") != -1:
                        if line.find("**kwargs") == -1:
                            self.add_message(
                                msgid="config-missing-kwargs-in-policy",
                                node=list(node.get_children())[idx],
                                confidence=None
                            )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if kwargs parameter in policies.")
            pass


class ClientHasApprovedMethodNamePrefix(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-approved-method-name-prefix"
    priority = -1
    msgs = {
        "C4720": (
            "Client is not using an approved method name prefix. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#service-operations",
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

    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientHasApprovedMethodNamePrefix, self).__init__(linter)

    def visit_classdef(self, node):
        """Visits every class in file and checks if it is a client. If it is a client, checks
        that approved method name prefixes are present.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """
        try:
            if node.name.endswith("Client") and node.name not in self.ignore_clients:
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
                            msgid="unapproved-client-method-name-prefix",
                            node=client_methods[idx],
                            confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client has approved method name prefix.")
            pass


class ClientMethodsUseKwargsWithMultipleParameters(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-method-multiple-parameters"
    priority = -1
    msgs = {
        "C4721": (
            "Client has too many positional arguments. Use keyword-only arguments."
            " See details: https://azure.github.io/azure-sdk/python_implementation.html#method-signatures",
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

    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientMethodsUseKwargsWithMultipleParameters, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that it doesn't have more than 5
        positional arguments.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.is_method() and node.parent.name not in self.ignore_clients:
                # Only bother checking method signatures with > 6 parameters (don't include self/cls/etc)
                if len(node.args.args) > 6:
                    positional_args = len(node.args.args) - len(node.args.defaults)
                    if positional_args > 6:
                        self.add_message(
                            msgid="client-method-has-more-than-5-positional-arguments", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if kwargs is used for multiple parameters.")
            pass

    visit_asyncfunctiondef = visit_functiondef


class ClientMethodsHaveTypeAnnotations(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-method-type-annotations"
    priority = -1
    msgs = {
        "C4722": (
            "Client method is missing type annotations/comments, return type annotations/comments, or "
            "mixing type annotations and comments. See details: "
            " https://azure.github.io/azure-sdk/python_implementation.html#types-or-not",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientMethodsHaveTypeAnnotations, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that all type comments/annotations
        and type returns are present.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.is_method() and node.parent.name not in self.ignore_clients:
                if not node.name.startswith("_") or node.name == "__init__":
                    # Checks that method has python 2/3 type comments or annotations as shown here:
                    # https://www.python.org/dev/peps/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code

                    # check for type comments
                    if node.type_comment_args is None or node.type_comment_returns is None:

                        # type annotations default to a list of None when not present,
                        # so need extra logic here to check for any hints that may be present
                        type_annotations = [type_hint for type_hint in node.args.annotations if type_hint is not None]

                        # check for type annotations
                        # node.args.args is a list of ast.AssignName arguments
                        # node.returns is the type annotation return
                        # Note that if the method returns nothing it will be of type ast.Const.NoneType
                        if (type_annotations == [] and len(node.args.args) > 1) or node.returns is None:
                            self.add_message(
                                msgid="client-method-missing-type-annotations", node=node, confidence=None
                            )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods missing type annotations.")
            pass

    visit_asyncfunctiondef = visit_functiondef


class ClientMethodsHaveTracingDecorators(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-method-has-tracing-decorator"
    priority = -1
    msgs = {
        "C4723": (
            "Client method is missing the distributed tracing decorator - `distributed_trace`. See details:"
            " https://azure.github.io/azure-sdk/python_implementation.html#distributed-tracing",
            "client-method-missing-tracing-decorator",
            "Client method should support distributed tracing.",
        ),
        "C4724": (
            "Client async method is missing the distributed tracing decorator - `distributed_trace_async`. "
            " See details: https://azure.github.io/azure-sdk/python_implementation.html#distributed-tracing",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientMethodsHaveTracingDecorators, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that a distributed tracing decorator is present.
        Ignores private methods, from_connection_string, and methods that retrieve child clients.

        node.decoratornames() returns a set of the method's decorator names.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.is_method() and not node.name.startswith("_") and \
                    node.parent.name not in self.ignore_clients:
                if node.args.kwarg and "azure.core.tracing.decorator.distributed_trace" not in node.decoratornames() \
                        and "builtins.classmethod" not in node.decoratornames():
                    self.add_message(
                        msgid="client-method-missing-tracing-decorator", node=node, confidence=None
                    )
        except AttributeError:
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every method in the client and checks that a distributed tracing decorator is present.
        Ignores private methods, from_connection_string, and methods that retrieve child clients.

        node.decoratornames() returns a set of the method's decorator names.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.is_method() and not node.name.startswith("_") and \
                    node.parent.name not in self.ignore_clients:
                if node.args.kwarg and "azure.core.tracing.decorator_async.distributed_trace_async" not in \
                        node.decoratornames() and "builtins.classmethod" not in node.decoratornames():
                    self.add_message(
                        msgid="client-method-missing-tracing-decorator-async", node=node, confidence=None
                    )
        except AttributeError:
            pass


class ClientsDoNotUseStaticMethods(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-does-not-use-static-methods"
    priority = -1
    msgs = {
        "C4725": (
            "Client should not use static methods (staticmethod). See details:"
            " https://azure.github.io/azure-sdk/python_implementation.html#method-signatures",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientsDoNotUseStaticMethods, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that it does not use staticmethod.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.is_method() and node.parent.name not in self.ignore_clients:
                # ignores private methods or methods that don't have any decorators
                if not node.name.startswith("_") and node.decorators is not None:
                    if "builtins.staticmethod" in node.decoratornames():
                        self.add_message(
                            msgid="client-method-should-not-use-static-method", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods do not use staticmethods.")
            pass

    visit_asyncfunctiondef = visit_functiondef


class FileHasCopyrightHeader(BaseChecker):
    __implements__ = IAstroidChecker

    name = "file-has-copyright-header"
    priority = -1
    msgs = {
        "C4726": (
            "File is missing a copyright header. See details:"
            " https://azure.github.io/azure-sdk/policies_opensource.html#",
            "file-needs-copyright-header",
            "Every source file should have a copyright header.",
        ),
    }
    options = (
        (
            "ignore-file-needs-copyright-header",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow file without a copyright header.",
            },
        ),
    )

    def __init__(self, linter=None):
        super(FileHasCopyrightHeader, self).__init__(linter)

    def visit_module(self, node):
        """Visits every file and checks that a copyright header is present.

        :param node: module node
        :type node: ast.Module
        :return: None
        """
        try:
            if not node.package:  # don't throw an error on an __init__.py file
                header = node.stream().read(200).lower()
                if header.find(b'copyright') == -1:
                    self.add_message(
                                msgid="file-needs-copyright-header", node=node, confidence=None
                            )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if file is missing a copyright header.")
            pass


class ClientUsesCorrectNamingConventions(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-naming-conventions"
    priority = -1
    msgs = {
        "C4727": (
            "Client is using an incorrect naming convention. See details:"
            " https://azure.github.io/azure-sdk/python_implementation.html#naming-conventions",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientUsesCorrectNamingConventions, self).__init__(linter)

    def visit_classdef(self, node):
        """Visits every class in file and checks if it is a client.
        Checks that correct naming convention is used for the client.
        Also checks that any class constants use uppercase.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """
        # check for correct capitalization for "Client" and whatever the first letter of the prefix is
        if "_" in node.name or node.name.endswith("client") or node.name[0] != node.name[0].upper():
            if not node.name.startswith("_") and node.name not in self.ignore_clients:
                self.add_message(
                    msgid="client-incorrect-naming-convention", node=node, confidence=None
                )

        # check for correct naming convention in any class constants
        if node.name.endswith("Client"):
            for idx in range(len(node.body)):
                try:
                    const_name = node.body[idx].targets[0].name
                    if const_name != const_name.upper():
                        self.add_message(
                            msgid="client-incorrect-naming-convention", node=node.body[idx], confidence=None
                        )
                except AttributeError:
                    logger.debug("Pylint custom checker failed to check if client uses correct naming conventions.")
                    pass

            # check that methods in client class do not use camelcase
            try:
                for func in node.body:
                    if func.name != func.name.lower() and not func.name.startswith("_"):
                        self.add_message(
                            msgid="client-incorrect-naming-convention", node=func, confidence=None
                        )
            except AttributeError:
                logger.debug("Pylint custom checker failed to check if client uses correct naming conventions.")
                pass


class ClientMethodsHaveKwargsParameter(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-methods-have-kwargs"
    priority = -1
    msgs = {
        "C4728": (
            "Client method is missing a **kwargs parameter. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientMethodsHaveKwargsParameter, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that it has a kwargs parameter.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.is_method() and node.parent.name not in self.ignore_clients:
                # avoid false positive with @property
                if node.decorators is not None:
                    if "builtins.property" in node.decoratornames():
                        return
                    if not node.name.startswith("_") and \
                            ("azure.core.tracing.decorator.distributed_trace" in node.decoratornames() or
                             "azure.core.tracing.decorator_async.distributed_trace_async" in node.decoratornames()):
                        if not node.args.kwarg:
                            self.add_message(
                                msgid="client-method-missing-kwargs", node=node, confidence=None
                            )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses kwargs parameter in method.")
            pass

    visit_asyncfunctiondef = visit_functiondef


class ClientMethodNamesDoNotUseDoubleUnderscorePrefix(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-methods-no-double-underscore"
    priority = -1
    msgs = {
        "C4729": (
            "Client method name should not use a double underscore prefix. See details:"
            " https://azure.github.io/azure-sdk/python_implementation.html#public-vs-private",
            "client-method-name-no-double-underscore",
            "Client method names should not use a leading double underscore prefix.",
        ),
    }
    options = (
        (
            "ignore-client-method-name-no-double-underscore",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client method to have double underscore prefix.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]
    acceptable_names = ["__init__", "__enter__", "__exit__", "__aenter__", "__aexit__", "__repr__"]

    def __init__(self, linter=None):
        super(ClientMethodNamesDoNotUseDoubleUnderscorePrefix, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that no name begins with a double underscore.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.is_method() and node.parent.name not in self.ignore_clients:
                if node.name.startswith("__") and node.name not in self.acceptable_names:
                    self.add_message(
                        msgid="client-method-name-no-double-underscore", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client method name does not use double underscore prefix.")
            pass

    visit_asyncfunctiondef = visit_functiondef


class ClientDocstringUsesLiteralIncludeForCodeExample(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-docstring-literal-include"
    priority = -1
    msgs = {
        "C4730": (
            "Client docstring should use a literal include directive for the code example. See details:"
            " https://azure.github.io/azure-sdk/python_documentation.html#code-snippets",
            "client-docstring-use-literal-include",
            "Client/methods should use literal include directives for code examples.",
        ),
    }
    options = (
        (
            "ignore-client-docstring-use-literal-include",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client to use code block.",
            },
        ),
    )

    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientDocstringUsesLiteralIncludeForCodeExample, self).__init__(linter)

    def visit_classdef(self, node):
        """Visits every class in file and checks if it is a client.
        Also checks that the class constructor uses literalinclude over a code-block for the code example.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """
        try:
            if node.name.endswith("Client") and node.name not in self.ignore_clients:
                if node.doc.find("code-block") != -1:
                    self.add_message(
                        msgid="client-docstring-use-literal-include", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses literalinclude over code-block.")
            pass

    def visit_functiondef(self, node):
        """Visits every method in the client class and checks that it uses literalinclude
         over a code-block for the code example.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.parent.name not in self.ignore_clients and node.is_method():
                if node.doc.find("code-block") != -1:
                    self.add_message(
                        msgid="client-docstring-use-literal-include", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses literalinclude over code-block.")
            pass

    visit_asyncfunctiondef = visit_functiondef


class AsyncClientCorrectNaming(BaseChecker):
    __implements__ = IAstroidChecker

    name = "async-client-correct-naming"
    priority = -1
    msgs = {
        "C4731": (
            "Async client should not include `Async` in the client name. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#async-support",
            "async-client-bad-name",
            "Async clients should not have async in the name.",
        ),
    }
    options = (
        (
            "ignore-async-client-bad-name",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow async client to include async in its name.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(AsyncClientCorrectNaming, self).__init__(linter)

    def visit_classdef(self, node):
        """Visits every class in file and checks that an async client does not use
        async in its name.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """
        try:
            # avoid false positive when async name is used with a base class.
            if node.name.endswith("Client") and "async" in node.name.lower() and "base" not in node.name.lower():
                if not node.name.startswith("_") and node.name not in self.ignore_clients:
                    self.add_message(
                        msgid="async-client-bad-name", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if async client uses correct naming.")
            pass


class SpecifyParameterNamesInCall(BaseChecker):
    __implements__ = IAstroidChecker

    name = "specify-parameter-names"
    priority = -1
    msgs = {
        "C4732": (
            "Specify the parameter names when calling methods with more than 2 required positional parameters."
            " See details: https://azure.github.io/azure-sdk/python_implementation.html#python-codestyle-positional-params",
            "specify-parameter-names-in-call",
            "You should specify the parameter names when the method has more than two positional arguments.",
        )
    }
    options = (
        (
            "ignore-specify-parameter-names-in-call",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Call the method without specifying parameter names.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(SpecifyParameterNamesInCall, self).__init__(linter)

    def visit_call(self, node):
        """Visits every call in the client and checks that it specifies the parameter name in
        the call if there are more than 2 require positional parameters.

        :param node: call node
        :type node: ast.Call
        :return: None
        """
        try:
            klass = node.parent.parent.parent
            function = node.parent.parent
            if klass.name.endswith("Client") and klass.name not in self.ignore_clients and function.is_method():
                # node.args represent positional arguments
                if len(node.args) > 2 and node.func.attrname != "format":
                    self.add_message(
                        msgid="specify-parameter-names-in-call", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods specify parameters name in call.")
            pass


class ClientListMethodsUseCorePaging(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-list-methods-use-paging"
    priority = -1
    msgs = {
        "C4733": (
            "Operations that return collections should return a value that implements the Paging protocol. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#response-formats",
            "client-list-methods-use-paging",
            "Client methods that return collections should use the Paging protocol.",
        ),
    }
    options = (
        (
            "ignore-client-list-methods-use-paging",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow collections method to not use paging protocol.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientListMethodsUseCorePaging, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that any list_ methods return
        an ItemPaged or AsyncItemPaged value.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.parent.name not in self.ignore_clients and node.is_method():
                if node.name.startswith("list"):
                    try:
                        # infer_call_result gives the method return value as a string
                        returns = next(node.infer_call_result()).as_string()
                        if returns.find("ItemPaged") == -1 and returns.find("AsyncItemPaged") == -1:
                            self.add_message(
                                msgid="client-list-methods-use-paging", node=node, confidence=None
                            )
                    except (astroid.exceptions.InferenceError, AttributeError): # astroid can't always infer the return
                        logger.debug("Pylint custom checker failed to check if client list method uses core paging.")
                        pass
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client list method uses core paging.")
            pass


class ClientLROMethodsUseCorePolling(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-lro-methods-use-polling"
    priority = -1
    msgs = {
        "C4734": (
            "Long running operations should return a value that implements the Poller protocol. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#response-formats",
            "client-lro-methods-use-polling",
            "Long running operations should use the polling protocol.",
        ),
    }
    options = (
        (
            "ignore-client-lro-methods-use-polling",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow LRO method to not use polling protocol.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientLROMethodsUseCorePolling, self).__init__(linter)

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that any begin_ methods return
        an LROPoller value.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if node.parent.name.endswith("Client") and node.parent.name not in self.ignore_clients and node.is_method():
                if node.name.startswith("begin"):
                    try:
                        # infer_call_result gives the method return value as a string
                        returns = next(node.infer_call_result()).as_string()
                        if returns.find("LROPoller") == -1:
                            self.add_message(
                                msgid="client-lro-methods-use-polling", node=node, confidence=None
                            )
                    except (astroid.exceptions.InferenceError, AttributeError): # astroid can't always infer the return
                        logger.debug("Pylint custom checker failed to check if client begin method uses core polling.")
                        pass
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client begin method uses core polling.")
            pass


class ClientLROMethodsUseCorrectNaming(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-lro-methods-use-correct-naming"
    priority = -1
    msgs = {
        "C4735": (
            "Methods that return an LROPoller should be prefixed with `begin_`. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#service-operations",
            "lro-methods-use-correct-naming",
            "Methods that return an LROPoller should be prefixed with `begin_`.",
        ),
    }
    options = (
        (
            "ignore-client-lro-methods-use-correct-naming",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow LRO method to use a different name.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientLROMethodsUseCorrectNaming, self).__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        """Visits every class in file and checks if it is a client.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """
        if node.name.endswith("Client") and node.name not in self.ignore_clients:
            self.is_client.append(True)
        else:
            self.is_client.append(False)

    def visit_return(self, node):
        if self.is_client and self.is_client[-1]:
            try:
                # check for a return value of LROPoller in client class
                if node.value.func.name == "LROPoller":
                    # get the method in which LROPoller is returned
                    method = node.value.func.scope()
                    if not method.name.startswith("begin") and not method.name.startswith("_"):
                        self.add_message(
                            msgid="lro-methods-use-correct-naming", node=method, confidence=None
                        )
            except AttributeError:
                logger.debug("Pylint custom checker failed to check if client method with polling uses correct naming.")
                pass


class ClientConstructorDoesNotHaveConnectionStringParam(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-conn-str-not-in-constructor"
    priority = -1
    msgs = {
        "C4736": (
            "The constructor must not take a connection string. See details: "
            "https://azure.github.io/azure-sdk/python_design.html#python-client-connection-string",
            "connection-string-should-not-be-constructor-param",
            "Client should have a method to create the client with a connection string.",
        ),
    }
    options = (
        (
            "ignore-connection-string-should-not-be-constructor-param",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client to use connection string param in constructor.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(ClientConstructorDoesNotHaveConnectionStringParam, self).__init__(linter)

    def visit_classdef(self, node):
        """Visits every class in file and checks if it is a client.
        If it is a client, it checks that a connection string parameter is not used in the constructor.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """
        try:
            if node.name.endswith("Client") and node.name not in self.ignore_clients:
                for func in node.body:
                    if func.name == "__init__":
                        for argument in func.args.args:
                            if argument.name == "connection_string" or argument.name == "conn_str":
                                self.add_message(
                                    msgid="connection-string-should-not-be-constructor-param", node=node, confidence=None
                                )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses connection string param in constructor.")
            pass


class PackageNameDoesNotUseUnderscoreOrPeriod(BaseChecker):
    __implements__ = IAstroidChecker

    name = "package-name-incorrect"
    priority = -1
    msgs = {
        "C4737": (
            "Package name should not use an underscore or period. Replace with dash (-). See details: "
            "https://azure.github.io/azure-sdk/python_design.html#packaging",
            "package-name-incorrect",
            "Package name should use dashes instead of underscore or period.",
        ),
    }
    options = (
        (
            "ignore-package-name-incorrect",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow package name to have a different naming convention.",
            },
        ),
    )

    def __init__(self, linter=None):
        super(PackageNameDoesNotUseUnderscoreOrPeriod, self).__init__(linter)

    def visit_module(self, node):
        """Visits setup.py and checks that its package name follows correct naming convention.

        :param node: module node
        :type node: ast.Module
        :return: None
        """
        try:
            if node.file.endswith("setup.py"):
                for nod in node.body:
                    if isinstance(nod, astroid.Assign):
                        if nod.targets[0].name == "PACKAGE_NAME":
                            package = nod.value
                            if package.value.find(".") != -1 or package.value.find("_") != -1:
                                self.add_message(
                                    msgid="package-name-incorrect", node=node, confidence=None
                                )
        except Exception:
            logger.debug("Pylint custom checker failed to check if package name is correct.")
            pass


class ServiceClientUsesNameWithClientSuffix(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-name-incorrect"
    priority = -1
    msgs = {
        "C4738": (
            "Service client types should use a `Client` suffix. See details: "
            "https://azure.github.io/azure-sdk/python_design.html#service-client",
            "client-suffix-needed",
            "Client should use the correct suffix.",
        ),
    }
    options = (
        (
            "ignore-client-suffix-needed",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow the client to have a different suffix.",
            },
        ),
    )

    def __init__(self, linter=None):
        super(ServiceClientUsesNameWithClientSuffix, self).__init__(linter)

    def visit_module(self, node):
        """Visits a file that has "client" in the file name and checks that the service client
        uses a `Client` suffix.

        :param node: module node
        :type node: ast.Module
        :return: None
        """
        try:
            # ignore base clients
            if node.file.endswith("base_client.py") or node.file.endswith("base_client_async.py"):
                return
            if node.file.endswith("client.py") or node.file.endswith("client_async.py"):
                has_client_suffix = False
                for idx in range(len(node.body)):
                    if isinstance(node.body[idx], astroid.ClassDef):
                        if node.body[idx].name.endswith("Client"):
                            has_client_suffix = True
                if has_client_suffix is False:
                    self.add_message(
                        msgid="client-suffix-needed", node=node, confidence=None
                    )
        except Exception:
            logger.debug("Pylint custom checker failed to check if service client has a client suffix.")
            pass


class CheckDocstringParameters(BaseChecker):
    __implements__ = IAstroidChecker

    name = "check-docstrings"
    priority = -1
    msgs = {
        "C4739": (
            'Params missing in docstring: "%s". See details: '
            'https://azure.github.io/azure-sdk/python_documentation.html#docstrings',
            "docstring-missing-param",
            "Docstring missing for param.",
        ),
        "C4740": (
            'Param types missing in docstring: "%s". See details: '
            'https://azure.github.io/azure-sdk/python_documentation.html#docstrings',
            "docstring-missing-type",
            "Docstring missing for param type.",
        ),
        "C4741": (
            "A return doc is missing in the docstring. See details: "
            "https://azure.github.io/azure-sdk/python_documentation.html#docstrings",
            "docstring-missing-return",
            "Docstring missing for return doc.",
        ),
        "C4742": (
            "A return type is missing in the docstring. See details: "
            "https://azure.github.io/azure-sdk/python_documentation.html#docstrings",
            "docstring-missing-rtype",
            "Docstring missing for return type.",
        ),
        "C4743": (
            '"%s" not found as a parameter. Use :keyword type myarg: if a keyword argument. See details: '
            'https://azure.github.io/azure-sdk/python_documentation.html#docstrings',
            "docstring-should-be-keyword",
            "Docstring should use keywords.",
        ),
    }
    options = (
        (
            "ignore-docstring-missing-param",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow a docstring param mismatch.",
            },
        ),
        (
            "ignore-docstring-missing-type",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow a docstring param type mismatch.",
            },
        ),
        (
            "ignore-docstring-missing-return",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow a docstring return doc mismatch",
            },
        ),
        (
            "ignore-docstring-missing-rtype",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow a docstring rtype mismatch",
            },
        ),
        (
            "ignore-docstring-should-be-keyword",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow a docstring to not use keyword for documentation.",
            },
        ),
    )

    def __init__(self, linter=None):
        super(CheckDocstringParameters, self).__init__(linter)

    def check_parameters(self, node):
        """Parse the docstring for any params and types
        and compares it to the function's parameters.

        Throws a pylint error if...
        1. Missing param in docstring.
        2. Missing a param type in the docstring.
        3. Missing a return doc in the docstring when a function returns something.
        4. Missing an rtype in the docstring when a function returns something.
        5. Extra params in docstring that aren't function parameters. Change to keywords.

        :param node: ast.ClassDef or ast.FunctionDef
        :return: None
        """
        arg_names = []
        # specific case for constructor where docstring found in class def
        if isinstance(node, astroid.ClassDef):
            for constructor in node.body:
                if isinstance(constructor, astroid.FunctionDef) and constructor.name == "__init__":
                    arg_names = [arg.name for arg in constructor.args.args]
                    break

        if isinstance(node, astroid.FunctionDef):
            arg_names = [arg.name for arg in node.args.args]

        try:
            # not every method will have a docstring so don't crash here, just return
            docstring = node.doc.split(":")
        except AttributeError:
            return

        docparams = {}
        for idx, line in enumerate(docstring):
            # this param has its type on a separate line
            if line.startswith("param") and line.count(" ") == 1:
                param = line.split("param ")[1]
                docparams[param] = None
            # this param has its type on the same line
            if line.startswith("param") and line.count(" ") == 2:
                _, param_type, param = line.split(" ")
                docparams[param] = param_type
            if line.startswith("type"):
                param = line.split("type ")[1]
                if param in docparams:
                    docparams[param] = docstring[idx+1]

        # check that all params are documented
        missing_params = []
        for param in arg_names:
            if param == "self" or param == "cls":
                continue
            if param not in docparams:
                missing_params.append(param)

        if missing_params:
            self.add_message(
                msgid="docstring-missing-param", args=(", ".join(missing_params)), node=node, confidence=None
            )

        # check if we have a type for each param and check if documented params that should be keywords
        missing_types = []
        should_be_keywords = []
        for param in docparams:
            if docparams[param] is None:
                missing_types.append(param)
            if param not in arg_names:
                should_be_keywords.append(param)

        if missing_types:
            self.add_message(
                msgid="docstring-missing-type", args=(", ".join(missing_types)), node=node, confidence=None
            )

        if should_be_keywords:
            self.add_message(
                msgid="docstring-should-be-keyword",
                args=(", ".join(should_be_keywords)),
                node=node,
                confidence=None
            )

    def check_return(self, node):
        """Checks if function returns anything.
        If return found, checks that the docstring contains a return doc and rtype.

        :param node: ast.FunctionDef
        :return: None
        """
        try:
            returns = next(node.infer_call_result()).as_string()
            if returns == "None":
                return
        except (astroid.exceptions.InferenceError, AttributeError):
            # this function doesn't return anything, just return
            return

        try:
            # not every method will have a docstring so don't crash here, just return
            docstring = node.doc.split(":")
        except AttributeError:
            return

        has_return, has_rtype = False, False
        for line in docstring:
            if line.startswith("return"):
                has_return = True
            if line.startswith("rtype"):
                has_rtype = True

        if has_return is False:
            self.add_message(
                msgid="docstring-missing-return", node=node, confidence=None
            )
        if has_rtype is False:
            self.add_message(
                msgid="docstring-missing-rtype", node=node, confidence=None
            )

    def visit_classdef(self, node):
        """Visits every class in the file and finds the constructor.
        Makes a call to compare class docstring with constructor params.

        :param node: ast.ClassDef
        :return: None
        """
        try:
            for func in node.body:
                if isinstance(func, astroid.FunctionDef) and func.name == "__init__":
                    self.check_parameters(node)
        except Exception:
            logger.debug("Pylint custom checker failed to check docstrings.")
            pass

    def visit_functiondef(self, node):
        """Visits every function in the file and makes calls
        to check docstring parameters and return statements.

        :param node: ast.FunctionDef
        :return: None
        """
        try:
            if node.name == "__init__":
                return
            self.check_parameters(node)
            self.check_return(node)
        except Exception:
            logger.debug("Pylint custom checker failed to check docstrings.")
            pass

    # this line makes it work for async functions
    visit_asyncfunctiondef = visit_functiondef


class CheckForPolicyUse(BaseChecker):
    __implements__ = IAstroidChecker

    name = "check-for-policies"
    priority = -1
    msgs = {
        "C4739": (
            "You should include a UserAgentPolicy in your HTTP pipeline. See details: "
            "https://azure.github.io/azure-sdk/python_implementation.html#network-operations",
            "missing-user-agent-policy",
            "You should include a UserAgentPolicy in the HTTP Pipeline.",
        ),
        "C4740": (
            "You should include a LoggingPolicy in your HTTP pipeline. See details: "
            "https://azure.github.io/azure-sdk/python_implementation.html#network-operations",
            "missing-logging-policy",
            "You should include a LoggingPolicy in the HTTP Pipeline.",
        ),
        "C4741": (
            "You should include a RetryPolicy in your HTTP pipeline. See details: "
            "https://azure.github.io/azure-sdk/python_implementation.html#network-operations",
            "missing-retry-policy",
            "You should include a RetryPolicy in the HTTP Pipeline.",
        ),
        "C4742": (
            "You should include a DistributedTracingPolicy in your HTTP pipeline. See details: "
            "https://azure.github.io/azure-sdk/python_implementation.html#network-operations",
            "missing-distributed-tracing-policy",
            "You should include a DistributedTracingPolicy in the HTTP Pipeline.",
        ),
    }
    options = (
        (
            "ignore-missing-user-agent-policy",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow the client to not have a UserAgentPolicy",
            },
        ),
        (
            "ignore-missing-logging-policy",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow the client to not have a LoggingPolicy",
            },
        ),
        (
            "ignore-missing-retry-policy",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow the client to not have a RetryPolicy",
            },
        ),
        (
            "ignore-missing-distributed-tracing-policy",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow the client to not have a DistributedTracingPolicy",
            },
        ),
    )

    def __init__(self, linter=None):
        super(CheckForPolicyUse, self).__init__(linter)
        self.node_to_use = None
        self.has_policies = set()
        self.ran_at_package_level = False
        self.disable_logging_error = False
        self.disable_user_agent_error = False
        self.disable_tracing_error = False
        self.disable_retry_error = False

    def visit_function(self, node, policy):
        """Visits the function and searches line by line for the policy being used.
        Also searches for if the policy came from the azure.core.configuration object.

        :param node: ast.FunctionDef
        :param policy: The policy imported in the file.
        :return: None
        """
        for func in node.body:
            if isinstance(func, astroid.FunctionDef):
                for idx, item in enumerate(func.body):
                    try:
                        line = list(node.get_children())[idx].as_string()
                        if line.find(policy) != -1:
                            self.has_policies.add(policy)
                        if line.find("config.logging_policy") != -1:
                            self.has_policies.add("NetworkTraceLoggingPolicy")
                        if line.find("config.retry_policy") != -1:
                            self.has_policies.add("RetryPolicy")
                        if line.find("config.user_agent_policy") != -1:
                            self.has_policies.add("UserAgentPolicy")
                    except IndexError:
                        pass

    def visit_class(self, klass, policy):
        """Visits any classes in the file and then makes a call
        to search its methods for the policy being used.

        :param klass: A class within the file
        :param policy: The policy imported in the file.
        :return: None
        """
        for idx, node in enumerate(klass):
            if isinstance(node, astroid.ClassDef):
                self.visit_function(node, policy)

    def visit_module(self, node):
        """Visits every file in the package and searches for policies as base classes
        or custom policies. If a core policy is imported in a file in calls helper
        methods to check that the policy was used in the code.

        This pylint checker is different from the others as it collects information across
        many files and then reports any errors. Due to this difference, disable commands
        must be searched for manually.

        :param node: ast.Module
        :return: None
        """
        # only throw the error if pylint was run at package level since it needs to check all the files
        # infer run location based on the location of the init file highest in dir hierarchy
        if node.package: # the init file
            count = node.file.split("azure-sdk-for-python")[1].count("-")
            if node.file.split("azure-sdk-for-python")[1].count("\\") <= (5 + count) and \
                    node.file.split("azure-sdk-for-python")[1].count("/") <= (5 + count):
                self.ran_at_package_level = True

        # not really a good place to throw the pylint error, so we'll do it on the init file.
        # By running this checker on all the files first and then reporting errors, pylint disables need to be
        # done manually for some reason
        if node.file.endswith("__init__.py") and self.node_to_use is None:
            header = node.stream().read(200).lower()
            if header.find(b'disable') != -1:
                if header.find(b'missing-logging-policy') != -1:
                    self.disable_logging_error = True
                if header.find(b'missing-user-agent-policy') != -1:
                    self.disable_user_agent_error = True
                if header.find(b'missing-distributed-tracing-policy') != -1:
                    self.disable_tracing_error = True
                if header.find(b'missing-retry-policy') != -1:
                    self.disable_retry_error = True
            self.node_to_use = node

        for idx in range(len(node.body)):
            # Check if the core policy is the base class for some custom policy, or a custom policy is being used
            # and we try our best to find it based on common naming conventions.
            if isinstance(node.body[idx], astroid.ClassDef):
                if "NetworkTraceLoggingPolicy" in node.body[idx].basenames:
                    self.has_policies.add("NetworkTraceLoggingPolicy")
                if node.body[idx].name.find("LoggingPolicy") != -1:
                    self.has_policies.add("NetworkTraceLoggingPolicy")
                if "RetryPolicy" in node.body[idx].basenames or "AsyncRetryPolicy" in node.body[idx].basenames:
                    self.has_policies.add("RetryPolicy")
                if node.body[idx].name.find("RetryPolicy") != -1:
                    self.has_policies.add("RetryPolicy")
                if "UserAgentPolicy" in node.body[idx].basenames:
                    self.has_policies.add("UserAgentPolicy")
                if node.body[idx].name.find("UserAgentPolicy") != -1:
                    self.has_policies.add("UserAgentPolicy")
                if "DistributedTracingPolicy" in node.body[idx].basenames:
                    self.has_policies.add("DistributedTracingPolicy")
                if node.body[idx].name.find("TracingPolicy") != -1:
                    self.has_policies.add("DistributedTracingPolicy")

            # policy is imported in this file, let's check that it gets used in the code
            if isinstance(node.body[idx], astroid.ImportFrom):
                for imp, pol in enumerate(node.body[idx].names):
                    if node.body[idx].names[imp][0].endswith("Policy") and \
                            node.body[idx].names[imp][0] not in self.has_policies:
                        self.visit_class(node.body, node.body[idx].names[imp][0])

    def close(self):
        """This method is inherited from BaseChecker and called at the very end of linting a module.
        It reports any errors and does a final check for any pylint disable statements.

        :return: None
        """
        if self.ran_at_package_level:
            if self.disable_logging_error is False:
                if "NetworkTraceLoggingPolicy" not in self.has_policies:
                    self.add_message(
                        msgid="missing-logging-policy", node=self.node_to_use, confidence=None
                    )
            if self.disable_retry_error is False:
                if "RetryPolicy" not in self.has_policies:
                    self.add_message(
                        msgid="missing-retry-policy", node=self.node_to_use, confidence=None
                    )
            if self.disable_user_agent_error is False:
                if "UserAgentPolicy" not in self.has_policies:
                    self.add_message(
                        msgid="missing-user-agent-policy", node=self.node_to_use, confidence=None
                    )
            if self.disable_tracing_error is False:
                if "DistributedTracingPolicy" not in self.has_policies:
                    self.add_message(
                        msgid="missing-distributed-tracing-policy", node=self.node_to_use, confidence=None
                    )


class CheckDocstringAdmonitionNewline(BaseChecker):
    __implements__ = IAstroidChecker

    name = "check-admonition"
    priority = -1
    msgs = {
        "C4744": (
            "The .. literalinclude statement needs a blank line above it. ",
            "docstring-admonition-needs-newline",
            "Put a newline after the example and before the literalinclude.",
        ),
    }
    options = (
        (
            "ignore-docstring-admonition-needs-newline",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow a docstring to not have newline after admonition example.",
            },
        ),
    )

    def __init__(self, linter=None):
        super(CheckDocstringAdmonitionNewline, self).__init__(linter)

    def check_for_admonition(self, node):
        """Parse the docstring for an admonition statement.
        If found, checks that the literalinclude statement has
        two newlines above it.

        :param node: ast.ClassDef or ast.FunctionDef
        :return: None
        """

        try:
            # not every class/method will have a docstring so don't crash here, just return
            if node.doc.find("admonition") != -1 and node.doc.find(".. literalinclude") != -1:
                literal_include = node.doc.split(".. literalinclude")[0]
                chars_list = list(reversed(literal_include))
                for idx, char in enumerate(chars_list):
                    if char == '\n':
                        if chars_list[idx+1] == '\n':
                            break
                        else:
                            self.add_message(
                                "docstring-admonition-needs-newline", node=node, confidence=None
                            )
                            break
        except Exception:
            return

    def visit_classdef(self, node):
        """Visits every class docstring.

        :param node: ast.ClassDef
        :return: None
        """
        try:
            for func in node.body:
                if isinstance(func, astroid.FunctionDef) and func.name == "__init__":
                    self.check_for_admonition(node)
        except Exception:
            logger.debug("Pylint custom checker failed to check docstrings.")
            pass

    def visit_functiondef(self, node):
        """Visits every method docstring.

        :param node: ast.FunctionDef
        :return: None
        """
        try:
            if node.name == "__init__":
                return
            self.check_for_admonition(node)
        except Exception:
            logger.debug("Pylint custom checker failed to check docstrings.")
            pass

    # this line makes it work for async functions
    visit_asyncfunctiondef = visit_functiondef


class CheckEnum(BaseChecker):
    __implements__ = IAstroidChecker

    name = "check-enum"
    priority = -1
    msgs = {
        "C4746": (
            "The enum must use uppercase naming. "
            "https://azure.github.io/azure-sdk/python_design.html#enumerations",
            "enum-must-be-uppercase",
            "Capitalize enum name.",
        ),
        "C4747":(
            "The enum must inherit from CaseInsensitiveEnumMeta. "
            "https://azure.github.io/azure-sdk/python_implementation.html#extensible-enumerations",
            "enum-must-inherit-case-insensitive-enum-meta",
            "Inherit CaseInsensitiveEnumMeta.",
        ),
    }
    options = (
        (
            "ignore-enum-must-be-uppercase",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow an enum to not be capitalized.",
            },
        ),
        (
            "ignore-enum-must-inherit-case-insensitive-enum-meta",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow an enum to not inherit CaseInsensitiveEnumMeta.",
            },
        ),
    )

    def __init__(self, linter=None):
        super(CheckEnum, self).__init__(linter)

    def visit_classdef(self, node):
        """Visits every enum class.

        :param node: ast.ClassDef
        :return: None
        """
        try:
            
            # If it has a metaclass, and is an enum class, check the capitalization
            if node.declared_metaclass():
                if node.declared_metaclass().name == "CaseInsensitiveEnumMeta":
                    self._enum_uppercase(node)   
            # Else if it does not have a metaclass, but it is an enum class
            # Check both capitalization and throw pylint error for metaclass
            elif node.bases[0].name == "str" and node.bases[1].name == "Enum":
                self.add_message(
                    "enum-must-inherit-case-insensitive-enum-meta", node=node, confidence=None
                )
                self._enum_uppercase(node)  

        except Exception:
            logger.debug("Pylint custom checker failed to check enum.")
            pass
    
    def _enum_uppercase(self, node):
        """Visits every enum within the class.
        Checks if the enum is uppercase, if it isn't it
        adds a pylint error message.

        :param node: ast.ClassDef
        :return: None
        """

        # Check capitalization of enums assigned in the class
        for nod in node.body:
            if isinstance(nod, astroid.Assign):
                if not nod.targets[0].name.isupper():
                    self.add_message(
                        "enum-must-be-uppercase", node=nod.targets[0], confidence=None
                    )


class CheckAPIVersion(BaseChecker):
    __implements__ = IAstroidChecker

    name = "check-api-version-kwarg"
    priority = -1
    msgs = {
        "C4748": (
            "The client constructor needs to take in an optional keyword-only api_version argument. "
            "https://azure.github.io/azure-sdk/python_design.html#specifying-the-service-version",
            "client-accepts-api-version-keyword",
            "Accept a keyword argument called api_version.",
        ),
    }
    options = (
        (
            "ignore-client-accepts-api-version-keyword",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow for no keyword api version.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient", "ARMPipelineClient", "AsyncARMPipelineClient"]

    def __init__(self, linter=None):
        super(CheckAPIVersion, self).__init__(linter)             

    def visit_classdef(self, node):
        """Visits every class in file and checks if it is a client.
        If it is a client, it checks that there is an api_version keyword.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """

        try:
            api_version = False
            
            if node.name.endswith("Client") and node.name not in self.ignore_clients:
                if node.doc:
                    if ":keyword api_version:" in node.doc or ":keyword str api_version:" in node.doc:
                        api_version = True
                if not api_version:    
                    for func in node.body:
                        if isinstance(func, astroid.FunctionDef):
                            if func.name == '__init__':
                                if func.doc: 
                                    if ":keyword api_version:" in func.doc or ":keyword str api_version:" in func.doc:
                                        api_version = True
                                if not api_version:
                                    self.add_message(
                                        msgid="client-accepts-api-version-keyword", node=node, confidence=None
                                    )   
    
      
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client takes in an optional keyword-only api_version argument.")
            pass                                                                                    


class CheckNamingMismatchGeneratedCode(BaseChecker):
    __implements__ = IAstroidChecker

    name = "check-naming-mismatch"
    priority = -1
    msgs = {
        "C4745": (
            "Do not alias generated code. "
            "This messes up sphinx, intellisense, and apiview, so please modify the name of the generated code through"
            " the swagger / directives, or code customizations. See Details: "
            "https://github.com/Azure/autorest/blob/main/docs/generate/built-in-directives.md",
            "naming-mismatch",
            "Do not alias models imported from the generated code.",
        ),
    }
    options = (
        (
            "ignore-naming-mismatch",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow generated code to be aliased.",
            },
        ),
    )

    def __init__(self, linter=None):
        super(CheckNamingMismatchGeneratedCode, self).__init__(linter)

    def visit_module(self, node):
        """Visits __init__.py and checks that there are not aliased models.

        :param node: module node
        :type node: ast.Module
        :return: None
        """
        try:
            if node.file.endswith("__init__.py"):
                aliased = []
            
                for nod in node.body:
                    if isinstance(nod, astroid.ImportFrom) or isinstance(nod, astroid.Import):
                        # If the model has been aliased
                        for name in nod.names:
                            if name[1] is not None:
                                aliased.append(name[1])

                for nod in node.body:
                    if isinstance(nod, astroid.Assign):
                        if nod.targets[0].as_string() == "__all__":
                            for models in nod.assigned_stmts():
                                for model_name in models.elts:
                                    if model_name.value in aliased:
                                        self.add_message(
                                            msgid="naming-mismatch", node=model_name, confidence=None
                                        )
    
        except Exception:
                logger.debug("Pylint custom checker failed to check if model is aliased.")
                pass


# if a linter is registered in this function then it will be checked with pylint
def register(linter):
    linter.register_checker(ClientsDoNotUseStaticMethods(linter))
    linter.register_checker(ClientConstructorTakesCorrectParameters(linter))
    linter.register_checker(ClientMethodsUseKwargsWithMultipleParameters(linter))
    linter.register_checker(ClientMethodsHaveTypeAnnotations(linter))
    linter.register_checker(ClientUsesCorrectNamingConventions(linter))
    linter.register_checker(ClientMethodsHaveKwargsParameter(linter))
    linter.register_checker(ClientHasKwargsInPoliciesForCreateConfigurationMethod(linter))
    linter.register_checker(AsyncClientCorrectNaming(linter))
    linter.register_checker(FileHasCopyrightHeader(linter))
    linter.register_checker(ClientMethodNamesDoNotUseDoubleUnderscorePrefix(linter))
    linter.register_checker(SpecifyParameterNamesInCall(linter))
    linter.register_checker(ClientConstructorDoesNotHaveConnectionStringParam(linter))
    linter.register_checker(PackageNameDoesNotUseUnderscoreOrPeriod(linter))
    linter.register_checker(ServiceClientUsesNameWithClientSuffix(linter))
    linter.register_checker(CheckDocstringAdmonitionNewline(linter))
    linter.register_checker(CheckNamingMismatchGeneratedCode(linter))
    linter.register_checker(CheckAPIVersion(linter))
    linter.register_checker(CheckEnum(linter))


    # disabled by default, use pylint --enable=check-docstrings if you want to use it
    linter.register_checker(CheckDocstringParameters(linter))

    # Rules are disabled until false positive rate improved
    # linter.register_checker(CheckForPolicyUse(linter))
    # linter.register_checker(ClientHasApprovedMethodNamePrefix(linter))
    # linter.register_checker(ClientMethodsHaveTracingDecorators(linter))
    # linter.register_checker(ClientDocstringUsesLiteralIncludeForCodeExample(linter))
    # linter.register_checker(ClientListMethodsUseCorePaging(linter))
    # linter.register_checker(ClientLROMethodsUseCorePolling(linter))
    # linter.register_checker(ClientLROMethodsUseCorrectNaming(linter))


