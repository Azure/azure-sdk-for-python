# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import absolute_import, division, print_function
"""
Pylint custom checkers for SDK guidelines: C4717 - C4737
"""

import logging
import astroid
import pylint.extensions._check_docs_utils as utils
from pylint.checkers import BaseChecker
from pylint.checkers import utils as checker_utils
from pylint.interfaces import IAstroidChecker
logger = logging.getLogger(__name__)


class ClientConstructorTakesCorrectParameters(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-constructor"
    priority = -1
    msgs = {
        "C4717": (
            "Client constructor is missing a credentials parameter. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods",
            "missing-client-constructor-parameter-credentials",
            "All client types should accept a credentials parameter.",
        ),
        "C4718": (
            "Client constructor is missing a **kwargs parameter. See details:"
            " https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits the constructor within a client class and checks that it has
        credentials and kwargs parameters.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
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
            " https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods",
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
                                msg_id="config-missing-kwargs-in-policy",
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

    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

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
                            msg_id="unapproved-client-method-name-prefix",
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
            " See details: https://azure.github.io/azure-sdk/python_introduction.html#method-signatures",
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

    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that it doesn't have more than 5
        positional arguments.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                # Only bother checking method signatures with > 6 parameters (don't include self/cls/etc)
                if len(node.args.args) > 6:
                    positional_args = len(node.args.args) - len(node.args.defaults)
                    if positional_args > 6:
                        self.add_message(
                            msg_id="client-method-has-more-than-5-positional-arguments", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if kwargs is used for multiple parameters.")
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every async method in the client and checks that it doesn't have more than 5
        positional arguments.

        :param node: function node
        :type node: ast.AsyncFunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                # Only bother checking method signatures with > 6 parameters (don't include self/cls/etc)
                if len(node.args.args) > 6:
                    positional_args = len(node.args.args) - len(node.args.defaults)
                    if positional_args > 6:
                        self.add_message(
                            msg_id="client-method-has-more-than-5-positional-arguments", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if kwargs is used for multiple parameters.")
            pass


class ClientMethodsHaveTypeAnnotations(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-method-type-annotations"
    priority = -1
    msgs = {
        "C4722": (
            "Client method is missing type annotations and/or return type annotations. See details:"
            " https://azure.github.io/azure-sdk/python_introduction.html#types-or-not",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that all type comments/annotations
        and type returns are present.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
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
                                msg_id="client-method-missing-type-annotations", node=node, confidence=None
                            )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods missing type annotations.")
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every async method in the client and checks that all type comments/annotations
        and type returns are present.

        :param node: function node
        :type node: ast.AsyncFunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                if not node.name.startswith("_") or node.name == "__init__":
                    # Checks that method has python 2/3 type comments or annotations as shown here:
                    # https://www.python.org/dev/peps/pep-0484/#suggested-syntax-for-python-2-7-and-straddling-code

                    # check for type comments
                    if node.type_comment_args is None or node.type_comment_returns is None:

                        # type annotations default to a list of None when not present,
                        # so need extra logic here to check for any hints that may be present
                        type_annotations = \
                            [type_hint for type_hint in node.args.annotations if type_hint is not None]

                        # check for type annotations
                        # node.args.args is a list of ast.AssignName arguments
                        # node.returns is the type annotation return
                        # Note that if the method returns nothing it will be of type ast.Const.NoneType
                        if (type_annotations == [] and len(node.args.args) > 1) or node.returns is None:
                            self.add_message(
                                msg_id="client-method-missing-type-annotations", node=node, confidence=None
                            )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods missing type annotations.")
            pass


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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that a distributed tracing decorator is present.
        Ignores private methods, from_connection_string, and methods that retrieve child clients.

        node.decoratornames() returns a set of the method's decorator names.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                # ignore private methods, client creation from connection string, and methods to retrieve child client
                if not node.name.startswith("_") and not node.name.startswith("from") \
                        and not node.name.endswith("_client"):
                    if "azure.core.tracing.decorator.distributed_trace" not in node.decoratornames():
                        self.add_message(
                            msg_id="client-method-missing-tracing-decorator", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods have tracing decorators.")
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every async method in the client and checks that a distributed tracing decorator is present.
        Ignores private methods, from_connection_string, and methods that retrieve child clients.

        node.decoratornames() returns a set of the method's decorator names.

        :param node: function node
        :type node: ast.AsyncFunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                # ignore private methods, client creation from connection string, and methods to retrieve child client
                if not node.name.startswith("_") and not node.name.startswith("from") \
                        and not node.name.endswith("_client"):
                    if "azure.core.tracing.decorator_async.distributed_trace_async" not in node.decoratornames():
                        self.add_message(
                            msg_id="client-method-missing-tracing-decorator-async", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods have tracing decorators.")
            pass


class ClientsDoNotUseStaticMethods(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-does-not-use-static-methods"
    priority = -1
    msgs = {
        "C4725": (
            "Client should not use static methods (staticmethod). See details:"
            " https://azure.github.io/azure-sdk/python_introduction.html#method-signatures",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that it does not use staticmethod.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                # ignores private methods or methods that don't have any decorators
                if not node.name.startswith("_") and node.decorators is not None:
                    if "builtins.staticmethod" in node.decoratornames():
                        self.add_message(
                            msg_id="client-method-should-not-use-static-method", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods do not use staticmethods.")
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every async method in the client and checks that it does not use staticmethod.

        :param node: function node
        :type node: ast.AsyncFunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                # ignores private methods or methods that don't have any decorators
                if not node.name.startswith("_") and node.decorators is not None:
                    if "builtins.staticmethod" in node.decoratornames():
                        self.add_message(
                            msg_id="client-method-should-not-use-static-method", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client methods do not use staticmethods.")
            pass


class FileHasCopyrightHeader(BaseChecker):
    __implements__ = IAstroidChecker

    name = "file-has-copyright-header"
    priority = -1
    msgs = {
        "C4726": (
            "File is missing a copyright header. See details:"
            " https://azure.github.io/azure-sdk/policies_opensource.html",
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
        super().__init__(linter)

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
                                msg_id="file-needs-copyright-header", node=node, confidence=None
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
            " https://azure.github.io/azure-sdk/python_introduction.html#naming-conventions",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

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
                    logger.debug("Pylint custom checker failed to check if client uses correct naming conventions.")
                    pass

    def visit_functiondef(self, node):
        """Visits every method in the client and checks for correct naming convention.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        # mainly just checks that method names don't use camelcase
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                if node.name != node.name.lower():
                    self.add_message(
                        msg_id="client-incorrect-naming-convention", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses correct naming conventions.")
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every async method in the client and checks for correct naming convention.

        :param node: function node
        :type node: ast.AsyncFunctionDef
        :return: None
        """
        # mainly just checks that method names don't use camelcase
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                if node.name != node.name.lower():
                    self.add_message(
                        msg_id="client-incorrect-naming-convention", node=node, confidence=None
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that it has a kwargs parameter.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                # avoid false positive with @property
                if node.decorators is not None and "builtins.property" in node.decoratornames():
                    return
                if not node.name.startswith("_"):
                    if not node.args.kwarg:
                        self.add_message(
                            msg_id="client-method-missing-kwargs", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses kwargs parameter in method.")
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every async method in the client and checks that it has a kwargs parameter.

        :param node: function node
        :type node: ast.AsyncFunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                # avoid false positive with @property
                if node.decorators is not None and "builtins.property" in node.decoratornames():
                    return
                if not node.name.startswith("_"):
                    if not node.args.kwarg:
                        self.add_message(
                            msg_id="client-method-missing-kwargs", node=node, confidence=None
                        )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses kwargs parameter in method.")
            pass


class ClientMethodNamesDoNotUseDoubleUnderscorePrefix(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-methods-no-double-underscore"
    priority = -1
    msgs = {
        "C4729": (
            "Client method name should not use a double underscore prefix. See details:"
            " https://azure.github.io/azure-sdk/python_introduction.html#public-vs-private",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]
    acceptable_names = ["__init__", "__enter__", "__exit__", "__aenter__", "__aexit__"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that no name begins with a double underscore.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                if node.name.startswith("__") and node.name not in self.acceptable_names:
                    self.add_message(
                        msg_id="client-method-name-no-double-underscore", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client method name does not use double underscore prefix.")
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every async method in the client and checks that no name begins with a double underscore.

        :param node: function node
        :type node: ast.AsyncFunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                if node.name.startswith("__") and node.name not in self.acceptable_names:
                    self.add_message(
                        msg_id="client-method-name-no-double-underscore", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client method name does not use double underscore prefix.")
            pass


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

    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []

    def visit_classdef(self, node):
        """Visits every class in file and checks if it is a client.
        Also checks that the class constructor uses literalinclude over a code-block for the code example.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """
        if node.name.endswith("Client") and node.name not in self.ignore_clients:
            self.is_client.append(True)
        else:
            self.is_client.append(False)

        try:
            if node.doc.find("code-block") != -1:
                self.add_message(
                    msg_id="client-docstring-use-literal-include", node=node, confidence=None
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
            if self.is_client and self.is_client[-1] and node.is_method():
                if node.doc.find("code-block") != -1:
                    self.add_message(
                        msg_id="client-docstring-use-literal-include", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses literalinclude over code-block.")
            pass

    def visit_asyncfunctiondef(self, node):
        """Visits every async method in the client class and checks that it uses literalinclude
         over a code-block for the code example.

        :param node: function node
        :type node: ast.AsyncFunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                if node.doc.find("code-block") != -1:
                    self.add_message(
                        msg_id="client-docstring-use-literal-include", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client uses literalinclude over code-block.")
            pass


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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)

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
                        msg_id="async-client-bad-name", node=node, confidence=None
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
            " See details: https://azure.github.io/azure-sdk/python_introduction.html#method-signatures",
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_call(self, node):
        """Visits every call in the client and checks that it specifies the parameter name in
        the call if there are more than 2 require positional parameters.

        :param node: call node
        :type node: ast.Call
        :return: None
        """
        try:
            # node.parent.parent is the method (ast.FunctionDef or ast.AsyncFunctionDef)
            if self.is_client and self.is_client[-1] and node.parent.parent.is_method():
                # node.args represent positional arguments
                if len(node.args) > 2:
                    self.add_message(
                        msg_id="specify-parameter-names-in-call", node=node, confidence=None
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that any list_ methods return
        an ItemPaged or AsyncItemPaged value.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                if node.name.startswith("list"):
                    try:
                        # infer_call_result gives as the method return value as a string
                        returns = next(node.infer_call_result()).as_string()
                        if returns.find("ItemPaged") == -1 and returns.find("AsyncItemPaged") == -1:
                            self.add_message(
                                msg_id="client-list-methods-use-paging", node=node, confidence=None
                            )
                    except astroid.exceptions.InferenceError:  # astroid can't always infer the return result
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that any begin_ methods return
        an LROPoller value.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method():
                if node.name.startswith("begin"):
                    try:
                        # infer_call_result gives as the method return value as a string
                        returns = next(node.infer_call_result()).as_string()
                        if returns.find("LROPoller") == -1:
                            self.add_message(
                                msg_id="client-lro-methods-use-polling", node=node, confidence=None
                            )
                    except astroid.exceptions.InferenceError:  # astroid can't always infer the return result
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
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
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

    def visit_functiondef(self, node):
        """Visits every method in the client and checks that any methods that return
        an LROPoller are named with a `begin` prefix.

        :param node: function node
        :type node: ast.FunctionDef
        :return: None
        """
        try:
            if self.is_client and self.is_client[-1] and node.is_method() and not node.name.startswith("_"):
                try:
                    # infer_call_result gives as the method return value as a string
                    returns = next(node.infer_call_result()).as_string()
                    if returns.find("LROPoller") != -1 and not \
                            isinstance(returns.find("LROPoller"), type(astroid.util.Uninferable)):
                        if not node.name.startswith("begin"):
                            self.add_message(
                                msg_id="lro-methods-use-correct-naming", node=node, confidence=None
                            )
                except astroid.exceptions.InferenceError:  # astroid can't always infer the return result
                    logger.debug("Pylint custom checker failed to check if client method with polling uses correct naming.")
                    pass
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client method with polling uses correct naming.")
            pass


class ClientHasFromConnectionStringMethod(BaseChecker):
    __implements__ = IAstroidChecker

    name = "client-has-from-connection-string-method"
    priority = -1
    msgs = {
        "C4736": (
            "Missing method to create the client with a connection string "
            "(disable me if client doesn't support connection strings). See details:"
            "https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods",
            "missing-client-creation-from-connection-string",
            "Client should have a method to create the client with a connection string.",
        ),
    }
    options = (
        (
            "ignore-missing-client-creation-from-connection-string",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow client to not have from_connection_string() method.",
            },
        ),
    )
    ignore_clients = ["PipelineClient", "AsyncPipelineClient"]

    def __init__(self, linter=None):
        super().__init__(linter)
        self.is_client = []
        self.is_async = False

    def visit_module(self, node):
        """Visits the file and checks if it is part of the async package.

        :param node: module node
        :type node: ast.Module
        :return: None
        """
        self.is_async = bool(node.file.find("aio") != -1)

    def visit_classdef(self, node):
        """Visits every class in file and checks if it is a client.
        If not part of the async package, checks that the client has a `from_connection_string`
        method present. Async package ignored to try to avoid false positives since it inherits
        from_connection_string from sync package.

        :param node: class node
        :type node: ast.ClassDef
        :return: None
        """
        if node.name.endswith("Client") and node.name not in self.ignore_clients:
            self.is_client.append(True)
        else:
            self.is_client.append(False)

        try:
            client_methods = set()
            if self.is_async is False:
                for func in node.body:
                    client_methods.add(func.name)

                if self.is_client and self.is_client[-1] and "from_connection_string" not in client_methods:
                    self.add_message(
                        msg_id="missing-client-creation-from-connection-string", node=node, confidence=None
                    )
        except AttributeError:
            logger.debug("Pylint custom checker failed to check if client has a from_connection_string method.")
            pass


class PackageNameDoesNotUseUnderscoreOrPeriod(BaseChecker):
    __implements__ = IAstroidChecker

    name = "package-name-incorrect"
    priority = -1
    msgs = {
        "C4737": (
            "Package name should not use an underscore or period. Replace with dash (-). See details: "
            "https://azure.github.io/azure-sdk/python_implementation.html#packaging",
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
        super().__init__(linter)

    def visit_module(self, node):
        """Visits a file and checks that its package name follows correct naming convention.

        :param node: module node
        :type node: ast.Module
        :return: None
        """
        try:
            # Get the package name
            path = node.file.replace('\\', '/')
            service = path.split("azure-sdk-for-python/sdk/")[1]
            package = service.split("/")[1]
            if package.find(".") != -1 or package.find("_") != -1:
                self.add_message(
                    msg_id="package-name-incorrect", node=node, confidence=None
                )
        except Exception:
            logger.debug("Pylint custom checker failed to check if package name is correct.")
            pass

# class LibraryProvidesLogging(BaseChecker):
#     __implements__ = IAstroidChecker
#
#     name = "library-provides-logging"
#     priority = -1
#     msgs = {
#         "C4736": (
#             "Library should provide logging at INFO, WARNING, ERROR, and DEBUG levels. See details:"
#             " https://azure.github.io/azure-sdk/python_implementation.html#logging",
#             "library-should-provide-loggers",
#             "Library should provide a named logger.",
#         )
#     }
#     options = (
#         (
#             "ignore-library-should-provide-loggers",
#             {
#                 "default": False,
#                 "type": "yn",
#                 "metavar": "<y_or_n>",
#                 "help": "Allow library to not have a named logger.",
#             },
#         ),
#     )
#
#     def __init__(self, linter=None):
#         super().__init__(linter)
#         self.logging_imported = False
#
#     def visit_classdef(self, node):
#         error, warning, info, debug = False, False, False, False
#         if node.name.lower().find("logging") != -1 or node.name.lower().find("logger") != -1:
#             for idx in range(len(node.body)):
#                 line = list(node.get_children())[idx].as_string()
#                 if line.find("isEnabledFor(logging.ERROR"): error = True
#                 if line.find("isEnabledFor(logging.WARNING"): warning = True
#                 if line.find("isEnabledFor(logging.INFO"): info = True
#                 if line.find("isEnabledFor(logging.DEBUG"): debug = True
#
#             if error and warning and info and debug:
#                 self.add_message(
#                     msg_id="library-should-provide-loggers", node=node, confidence=None
#                 )
#
#
# class ClientExceptionsDeriveFromCore(BaseChecker):
#     __implements__ = IAstroidChecker
#
#     name = "client-exceptions-derive-from-core"
#     priority = -1
#     msgs = {
#         "C4735": (
#             "Client exceptions should be based on existing exception types present in azure-core. See details:"
#             " https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-error-handling",
#             "client-bad-exception-type",
#             "All client exceptions should derive from azure-core.",
#         ),
#     }
#     options = (
#         (
#             "ignore-client-bad-exception-type",
#             {
#                 "default": False,
#                 "type": "yn",
#                 "metavar": "<y_or_n>",
#                 "help": "Allow client to have new exception type.",
#             },
#         ),
#     )
#     ignore_clients = ["PipelineClient", "AsyncPipelineClient"]
#
#     def __init__(self, linter=None):
#         super().__init__(linter)
#         # self.is_client = []

    # def visit_classdef(self, node):
    #     if node.name.endswith("Client") and node.name not in self.ignore_clients:
    #         self.is_client.append(True)
    #     else:
    #         self.is_client.append(False)
    #
    # def visit_functiondef(self, node):
    #     try:
    #         if self.is_client and self.is_client[-1] and node.is_method():
    #             # returns = next(node.infer_call_result()).as_string()
    #             self.add_message(
    #                 msg_id="client-bad-exception-type", node=node, confidence=None
    #             )
    #     except AttributeError:
    #         logger.debug("this isn' working")

    # def visit_classdef(self, node):
    #     if node.name.endswith("Error") or node.name.endswith("Exception"):
    #         core_exception = [ex for ex in node.bases if ex.name == "HttpResponseError"]
    #         if not core_exception:
    #             self.add_message(
    #                 msg_id="client-bad-exception-type", node=node, confidence=None
    #             )


class DocstringParameterCheckerCustom(BaseChecker):
    """Checker for Sphinx, Google, or Numpy style docstrings
    * Check that all function, method and constructor parameters are mentioned
      in the params and types part of the docstring.  Constructor parameters
      can be documented in either the class docstring or ``__init__`` docstring,
      but not both.
    * Check that there are no naming inconsistencies between the signature and
      the documentation, i.e. also report documented parameters that are missing
      in the signature. This is important to find cases where parameters are
      renamed only in the code, not in the documentation.
    * Check that all explicitly raised exceptions in a function are documented
      in the function docstring. Caught exceptions are ignored.
    Activate this checker by adding the line::
        load-plugins=pylint.extensions.docparams
    to the ``MASTER`` section of your ``.pylintrc``.
    :param linter: linter object
    :type linter: :class:`pylint.lint.PyLinter`
    """

    __implements__ = IAstroidChecker

    name = "parameter_documentation"
    msgs = {
        "W9005": (
            '"%s" has constructor parameters documented in class and __init__',
            "multiple-constructor-doc",
            "Please remove parameter declarations in the class or constructor.",
        ),
        "W9006": (
            '"%s" not documented as being raised',
            "missing-raises-doc",
            "Please document exceptions for all raised exception types.",
        ),
        "W9008": (
            "Redundant returns documentation",
            "redundant-returns-doc",
            "Please remove the return/rtype documentation from this method.",
        ),
        "W9010": (
            "Redundant yields documentation",
            "redundant-yields-doc",
            "Please remove the yields documentation from this method.",
        ),
        "W9011": (
            "Missing return documentation",
            "missing-return-doc",
            "Please add documentation about what this method returns.",
            {"old_names": [("W9007", "missing-returns-doc")]},
        ),
        "W9012": (
            "Missing return type documentation",
            "missing-return-type-doc",
            "Please document the type returned by this method.",
            # we can't use the same old_name for two different warnings
            # {'old_names': [('W9007', 'missing-returns-doc')]},
        ),
        "W9013": (
            "Missing yield documentation",
            "missing-yield-doc",
            "Please add documentation about what this generator yields.",
            {"old_names": [("W9009", "missing-yields-doc")]},
        ),
        "W9014": (
            "Missing yield type documentation",
            "missing-yield-type-doc",
            "Please document the type yielded by this method.",
            # we can't use the same old_name for two different warnings
            # {'old_names': [('W9009', 'missing-yields-doc')]},
        ),
        "W9015": (
            '"%s" missing in parameter documentation',
            "missing-param-doc",
            "Please add parameter declarations for all parameters.",
            {"old_names": [("W9003", "missing-param-doc")]},
        ),
        "W9016": (
            '"%s" missing in parameter type documentation',
            "missing-type-doc",
            "Please add parameter type declarations for all parameters.",
            {"old_names": [("W9004", "missing-type-doc")]},
        ),
        "W9017": (
            '"%s" differing in parameter documentation. Did you mean to use :keyword: instead of :param:?',
            "differing-param-doc-custom",
            "Please check parameter names in declarations.",
        ),
    }

    options = (
        (
            "accept-no-param-doc",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Whether to accept totally missing parameter "
                "documentation in the docstring of a function that has "
                "parameters.",
            },
        ),
        (
            "accept-no-raise-doc",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Whether to accept totally missing raises "
                "documentation in the docstring of a function that "
                "raises an exception.",
            },
        ),
        (
            "accept-no-return-doc",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Whether to accept totally missing return "
                "documentation in the docstring of a function that "
                "returns a statement.",
            },
        ),
        (
            "accept-no-yields-doc",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Whether to accept totally missing yields "
                "documentation in the docstring of a generator.",
            },
        ),
        (
            "default-docstring-type",
            {
                "type": "choice",
                "default": "default",
                "choices": list(utils.DOCSTRING_TYPES),
                "help": "If the docstring type cannot be guessed "
                "the specified docstring type will be used.",
            },
        ),
    )

    priority = -2

    constructor_names = {"__init__", "__new__"}
    not_needed_param_in_docstring = {"self", "cls", "kwargs"}

    def visit_functiondef(self, node):
        """Called for function and method definitions (def).
        :param node: Node for a function or method definition in the AST
        :type node: :class:`astroid.scoped_nodes.Function`
        """
        try:
            node.doc = node.doc.replace(":keyword", ":var")
        except AttributeError:
            pass
        node_doc = utils.docstringify(node.doc, self.config.default_docstring_type)
        self.check_functiondef_params(node, node_doc)

    def check_functiondef_params(self, node, node_doc):
        node_allow_no_param = None
        if node.name in self.constructor_names:
            class_node = checker_utils.node_frame_class(node)
            try:
                class_node.doc = class_node.doc.replace(":keyword", ":var")
            except AttributeError:
                pass
            if class_node is not None:
                class_doc = utils.docstringify(
                    class_node.doc, self.config.default_docstring_type
                )

                self.check_single_constructor_params(class_doc, node_doc, class_node)

                # __init__ or class docstrings can have no parameters documented
                # as long as the other documents them.
                node_allow_no_param = (
                    class_doc.has_params()
                    or class_doc.params_documented_elsewhere()
                    or None
                )
                class_allow_no_param = (
                    node_doc.has_params()
                    or node_doc.params_documented_elsewhere()
                    or None
                )

                self.check_arguments_in_docstring(
                    class_doc, node.args, class_node, class_allow_no_param
                )

        self.check_arguments_in_docstring(
            node_doc, node.args, node, node_allow_no_param
        )

    def visit_raise(self, node):
        func_node = node.frame()
        if not isinstance(func_node, astroid.FunctionDef):
            return

        expected_excs = utils.possible_exc_types(node)

        if not expected_excs:
            return

        if not func_node.doc:
            # If this is a property setter,
            # the property should have the docstring instead.
            property_ = utils.get_setters_property(func_node)
            if property_:
                func_node = property_

        doc = utils.docstringify(func_node.doc, self.config.default_docstring_type)
        if not doc.is_valid():
            if doc.doc:
                self._handle_no_raise_doc(expected_excs, func_node)
            return

        found_excs_full_names = doc.exceptions()

        # Extract just the class name, e.g. "error" from "re.error"
        found_excs_class_names = {exc.split(".")[-1] for exc in found_excs_full_names}
        missing_excs = expected_excs - found_excs_class_names
        self._add_raise_message(missing_excs, func_node)

    def visit_return(self, node):
        if not utils.returns_something(node):
            return

        func_node = node.frame()
        if not isinstance(func_node, astroid.FunctionDef):
            return

        doc = utils.docstringify(func_node.doc, self.config.default_docstring_type)
        if not doc.is_valid() and self.config.accept_no_return_doc:
            return

        is_property = checker_utils.decorated_with_property(func_node)

        if not (doc.has_returns() or (doc.has_property_returns() and is_property)):
            self.add_message("missing-return-doc", node=func_node)

        if func_node.returns:
            return

        if not (doc.has_rtype() or (doc.has_property_type() and is_property)):
            self.add_message("missing-return-type-doc", node=func_node)

    def visit_yield(self, node):
        func_node = node.frame()
        if not isinstance(func_node, astroid.FunctionDef):
            return

        doc = utils.docstringify(func_node.doc, self.config.default_docstring_type)
        if not doc.is_valid() and self.config.accept_no_yields_doc:
            return

        if doc.supports_yields:
            doc_has_yields = doc.has_yields()
            doc_has_yields_type = doc.has_yields_type()
        else:
            doc_has_yields = doc.has_returns()
            doc_has_yields_type = doc.has_rtype()

        if not doc_has_yields:
            self.add_message("missing-yield-doc", node=func_node)

        if not doc_has_yields_type:
            self.add_message("missing-yield-type-doc", node=func_node)

    def visit_yieldfrom(self, node):
        self.visit_yield(node)

    def check_arguments_in_docstring(
        self, doc, arguments_node, warning_node, accept_no_param_doc=None
    ):
        """Check that all parameters in a function, method or class constructor
        on the one hand and the parameters mentioned in the parameter
        documentation (e.g. the Sphinx tags 'param' and 'type') on the other
        hand are consistent with each other.
        * Undocumented parameters except 'self' are noticed.
        * Undocumented parameter types except for 'self' and the ``*<args>``
          and ``**<kwargs>`` parameters are noticed.
        * Parameters mentioned in the parameter documentation that don't or no
          longer exist in the function parameter list are noticed.
        * If the text "For the parameters, see" or "For the other parameters,
          see" (ignoring additional whitespace) is mentioned in the docstring,
          missing parameter documentation is tolerated.
        * If there's no Sphinx style, Google style or NumPy style parameter
          documentation at all, i.e. ``:param`` is never mentioned etc., the
          checker assumes that the parameters are documented in another format
          and the absence is tolerated.
        :param doc: Docstring for the function, method or class.
        :type doc: str
        :param arguments_node: Arguments node for the function, method or
            class constructor.
        :type arguments_node: :class:`astroid.scoped_nodes.Arguments`
        :param warning_node: The node to assign the warnings to
        :type warning_node: :class:`astroid.scoped_nodes.Node`
        :param accept_no_param_doc: Whether or not to allow no parameters
            to be documented.
            If None then this value is read from the configuration.
        :type accept_no_param_doc: bool or None
        """
        # Tolerate missing param or type declarations if there is a link to
        # another method carrying the same name.
        if not doc.doc:
            return

        if accept_no_param_doc is None:
            accept_no_param_doc = self.config.accept_no_param_doc
        tolerate_missing_params = doc.params_documented_elsewhere()

        # Collect the function arguments.
        expected_argument_names = {arg.name for arg in arguments_node.args}
        expected_argument_names.update(arg.name for arg in arguments_node.kwonlyargs)
        not_needed_type_in_docstring = self.not_needed_param_in_docstring.copy()

        if arguments_node.vararg is not None:
            expected_argument_names.add(arguments_node.vararg)
            not_needed_type_in_docstring.add(arguments_node.vararg)
        if arguments_node.kwarg is not None:
            expected_argument_names.add(arguments_node.kwarg)
            not_needed_type_in_docstring.add(arguments_node.kwarg)

        params_with_doc, params_with_type = doc.match_param_docs()
        # Tolerate no parameter documentation at all.
        if not params_with_doc and not params_with_type and accept_no_param_doc:
            tolerate_missing_params = True

        def _compare_missing_args(found_argument_names, message_id, not_needed_names):
            """Compare the found argument names with the expected ones and
            generate a message if there are arguments missing.
            :param set found_argument_names: argument names found in the
                docstring
            :param str message_id: pylint message id
            :param not_needed_names: names that may be omitted
            :type not_needed_names: set of str
            """
            if not tolerate_missing_params:
                missing_argument_names = (
                    expected_argument_names - found_argument_names
                ) - not_needed_names
                if missing_argument_names:
                    self.add_message(
                        message_id,
                        args=(", ".join(sorted(missing_argument_names)),),
                        node=warning_node,
                    )

        def _compare_different_args(found_argument_names, message_id, not_needed_names):
            """Compare the found argument names with the expected ones and
            generate a message if there are extra arguments found.
            :param set found_argument_names: argument names found in the
                docstring
            :param str message_id: pylint message id
            :param not_needed_names: names that may be omitted
            :type not_needed_names: set of str
            """
            differing_argument_names = (
                (expected_argument_names ^ found_argument_names)
                - not_needed_names
                - expected_argument_names
            )

            if differing_argument_names:
                self.add_message(
                    message_id,
                    args=(", ".join(sorted(differing_argument_names)),),
                    node=warning_node,
                )

        _compare_missing_args(
            params_with_doc, "missing-param-doc", self.not_needed_param_in_docstring
        )

        for index, arg_name in enumerate(arguments_node.args):
            if arguments_node.annotations[index]:
                params_with_type.add(arg_name.name)

        _compare_missing_args(
            params_with_type, "missing-type-doc", not_needed_type_in_docstring
        )

        _compare_different_args(
            params_with_doc, "differing-param-doc-custom", self.not_needed_param_in_docstring
        )

    def check_single_constructor_params(self, class_doc, init_doc, class_node):
        if class_doc.has_params() and init_doc.has_params():
            self.add_message(
                "multiple-constructor-doc", args=(class_node.name,), node=class_node
            )

    def _handle_no_raise_doc(self, excs, node):
        if self.config.accept_no_raise_doc:
            return

        self._add_raise_message(excs, node)

    def _add_raise_message(self, missing_excs, node):
        """
        Adds a message on :param:`node` for the missing exception type.
        :param missing_excs: A list of missing exception types.
        :type missing_excs: set(str)
        :param node: The node show the message on.
        :type node: astroid.node_classes.NodeNG
        """
        if node.is_abstract():
            try:
                missing_excs.remove("NotImplementedError")
            except KeyError:
                pass

        if not missing_excs:
            return

        self.add_message(
            "missing-raises-doc", args=(", ".join(sorted(missing_excs)),), node=node
        )


def register(linter):
    linter.register_checker(ClientMethodsHaveTracingDecorators(linter))
    linter.register_checker(ClientsDoNotUseStaticMethods(linter))
    # linter.register_checker(ClientHasApprovedMethodNamePrefix(linter))
    linter.register_checker(ClientConstructorTakesCorrectParameters(linter))
    linter.register_checker(ClientMethodsUseKwargsWithMultipleParameters(linter))
    linter.register_checker(ClientMethodsHaveTypeAnnotations(linter))
    linter.register_checker(ClientUsesCorrectNamingConventions(linter))
    # linter.register_checker(ClientMethodsHaveKwargsParameter(linter))
    linter.register_checker(ClientHasKwargsInPoliciesForCreateConfigurationMethod(linter))
    linter.register_checker(AsyncClientCorrectNaming(linter))
    linter.register_checker(FileHasCopyrightHeader(linter))
    linter.register_checker(ClientMethodNamesDoNotUseDoubleUnderscorePrefix(linter))
    linter.register_checker(ClientDocstringUsesLiteralIncludeForCodeExample(linter))
    linter.register_checker(SpecifyParameterNamesInCall(linter))
    linter.register_checker(ClientListMethodsUseCorePaging(linter))
    linter.register_checker(ClientLROMethodsUseCorePolling(linter))
    linter.register_checker(ClientLROMethodsUseCorrectNaming(linter))
    linter.register_checker(ClientHasFromConnectionStringMethod(linter))
    linter.register_checker(PackageNameDoesNotUseUnderscoreOrPeriod(linter))
    # linter.register_checker(LibraryProvidesLogging(linter))
    # linter.register_checker(ClientExceptionsDeriveFromCore(linter))
    linter.register_checker(DocstringParameterCheckerCustom(linter))