# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import astroid
import pylint.testutils
import requests

from azure.core import PipelineClient
from azure.core.configuration import Configuration
from pylint_custom_plugin import pylint_guidelines_checker as checker

class TestClientMethodsHaveTracingDecorators(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientMethodsHaveTracingDecorators

    def test_ignores_constructor(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_private_method(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def _private_method(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_private_method_async(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            async def _private_method(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node)

    def test_ignores_methods_with_decorators(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        from azure.core.tracing.decorator import distributed_trace
        class SomeClient(): #@
            @distributed_trace
            def create_configuration(self, **kwargs): #@
                pass
            @distributed_trace
            def get_thing(self, **kwargs): #@
                pass
            @distributed_trace
            def list_thing(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_functiondef(func_node_b)
            self.checker.visit_functiondef(func_node_c)

    def test_ignores_async_methods_with_decorators(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        from azure.core.tracing.decorator_async import distributed_trace_async
        class SomeClient(): #@
            @distributed_trace_async
            async def create_configuration(self, **kwargs): #@
                pass
            @distributed_trace_async
            async def get_thing(self, **kwargs): #@
                pass
            @distributed_trace_async
            async def list_thing(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)
            self.checker.visit_asyncfunctiondef(func_node_c)

    def test_finds_sync_decorator_on_async_method(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        from azure.core.tracing.decorator import distributed_trace
        class SomeClient(): #@
            @distributed_trace
            async def create_configuration(self, **kwargs): #@
                pass
            @distributed_trace
            async def get_thing(self, **kwargs): #@
                pass
            @distributed_trace
            async def list_thing(self, **kwargs): #@
                pass
        """)
        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-tracing-decorator-async", node=func_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-tracing-decorator-async", node=func_node_b
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-tracing-decorator-async", node=func_node_c
            ),
        ):
            self.checker.visit_asyncfunctiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)
            self.checker.visit_asyncfunctiondef(func_node_c)

    def test_finds_async_decorator_on_sync_method(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        from azure.core.tracing.decorator_async import distributed_trace_async
        class SomeClient(): #@
            @distributed_trace_async
            def create_configuration(self, **kwargs): #@
                pass
            @distributed_trace_async
            def get_thing(self, **kwargs): #@
                pass
            @distributed_trace_async
            def list_thing(self, **kwargs): #@
                pass
        """)
        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-tracing-decorator", node=func_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-tracing-decorator", node=func_node_b
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-tracing-decorator", node=func_node_c
            ),
        ):
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_functiondef(func_node_b)
            self.checker.visit_functiondef(func_node_c)

    def test_ignores_other_decorators(self):
        class_node, func_node_a, func_node_b = astroid.extract_node(
            """
        from azure.core.tracing.decorator import distributed_trace
        class SomeClient(): #@
            @classmethod
            @distributed_trace
            def download_thing(self, some, **kwargs): #@
                pass

            @distributed_trace
            @decorator
            def do_thing(self, some, **kwargs): #@
                pass
        """
        )

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_functiondef(func_node_b)

    def test_ignores_other_decorators_async(self):
        class_node, func_node_a, func_node_b = astroid.extract_node(
            """
        from azure.core.tracing.decorator_async import distributed_trace_async
        class SomeClient(): #@
            @classmethod
            @distributed_trace_async
            async def download_thing(self, some, **kwargs): #@
                pass

            @distributed_trace_async
            @decorator
            async def do_thing(self, some, **kwargs): #@
                pass
        """
        )

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)

    def test_ignores_non_client_method(self):
        class_node, func_node_a, func_node_b = astroid.extract_node(
            """
        class SomethingElse(): #@
            def download_thing(self, some, **kwargs): #@
                pass
            
            @classmethod
            async def do_thing(self, some, **kwargs): #@
                pass
        """
        )

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_implementation.html#distributed-tracing"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientsDoNotUseStaticMethods(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientsDoNotUseStaticMethods

    def test_ignores_constructor(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_private_method(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            @staticmethod
            def _private_method(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_private_method_async(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            @staticmethod
            async def _private_method(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node)

    def test_ignores_methods_with_other_decorators(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace
            def create_configuration(self): #@
                pass
            @distributed_trace
            def get_thing(self): #@
                pass
            @distributed_trace
            def list_thing(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_functiondef(func_node_b)
            self.checker.visit_functiondef(func_node_c)

    def test_ignores_async_methods_with_other_decorators(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace_async
            async def create_configuration(self): #@
                pass
            @distributed_trace_async
            async def get_thing(self): #@
                pass
            @distributed_trace_async
            async def list_thing(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)
            self.checker.visit_asyncfunctiondef(func_node_c)

    def test_finds_staticmethod_on_async_method(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        class SomeClient(): #@
            @staticmethod
            async def create_configuration(self): #@
                pass
            @staticmethod
            async def get_thing(self): #@
                pass
            @staticmethod
            async def list_thing(self): #@
                pass
        """)
        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-method-should-not-use-static-method", node=func_node_a
                ),
                pylint.testutils.Message(
                    msg_id="client-method-should-not-use-static-method", node=func_node_b
                ),
                pylint.testutils.Message(
                    msg_id="client-method-should-not-use-static-method", node=func_node_c
                ),
        ):
            self.checker.visit_asyncfunctiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)
            self.checker.visit_asyncfunctiondef(func_node_c)

    def test_finds_staticmethod_on_sync_method(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        class SomeClient(): #@
            @staticmethod
            def create_configuration(self): #@
                pass
            @staticmethod
            def get_thing(self): #@
                pass
            @staticmethod
            def list_thing(self): #@
                pass
        """)
        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-method-should-not-use-static-method", node=func_node_a
                ),
                pylint.testutils.Message(
                    msg_id="client-method-should-not-use-static-method", node=func_node_b
                ),
                pylint.testutils.Message(
                    msg_id="client-method-should-not-use-static-method", node=func_node_c
                ),
        ):
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_functiondef(func_node_b)
            self.checker.visit_functiondef(func_node_c)

    def test_ignores_other_multiple_decorators(self):
        class_node, func_node_a, func_node_b = astroid.extract_node(
            """
        class SomeClient(): #@
            @classmethod
            @distributed_trace
            def download_thing(self, some, **kwargs): #@
                pass

            @distributed_trace
            @decorator
            def do_thing(self, some, **kwargs): #@
                pass
        """
        )

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_functiondef(func_node_b)

    def test_ignores_other_multiple_decorators_async(self):
        class_node, func_node_a, func_node_b = astroid.extract_node(
            """
        class SomeClient(): #@
            @classmethod
            @distributed_trace_async
            async def download_thing(self, some, **kwargs): #@
                pass

            @distributed_trace_async
            @decorator
            async def do_thing(self, some, **kwargs): #@
                pass
        """
        )

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)

    def test_ignores_non_client_method(self):
        class_node, func_node_a, func_node_b = astroid.extract_node(
            """
        class SomethingElse(): #@
            @staticmethod
            def download_thing(self, some, **kwargs): #@
                pass

            @staticmethod
            async def do_thing(self, some, **kwargs): #@
                pass
        """
        )

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_implementation.html#method-signatures"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientHasApprovedMethodNamePrefix(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientHasApprovedMethodNamePrefix

    def test_ignores_constructor(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_private_method(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def _private_method(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_if_exists_suffix(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def check_if_exists(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_from_prefix(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def from_connection_string(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_approved_prefix_names(self):
        class_node, func_node_a, func_node_b, func_node_c, func_node_d, func_node_e, func_node_f, func_node_g, \
            func_node_h, func_node_i, func_node_j, func_node_k, func_node_l = astroid.extract_node("""
        class SomeClient(): #@
            def create_configuration(self): #@
                pass
            def get_thing(self): #@
                pass
            def list_thing(self): #@
                pass
            def upsert_thing(self): #@
                pass
            def set_thing(self): #@
                pass
            def update_thing(self): #@
                pass
            def replace_thing(self): #@
                pass
            def append_thing(self): #@
                pass
            def add_thing(self): #@
                pass
            def delete_thing(self): #@
                pass
            def remove_thing(self): #@
                pass
            def begin_thing(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_non_client_with_unapproved_prefix_names(self):
        class_node, function_node = astroid.extract_node(
            """
        class SomethingElse(): #@
            def download_thing(self, some, **kwargs): #@
                pass
        """
        )

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_nested_function_with_unapproved_prefix_names(self):
        class_node, function_node = astroid.extract_node(
            """
            class SomeClient(): #@
                def create_configuration(self, **kwargs): #@
                    def nested(hello, world):
                        pass
            """
        )

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_finds_unapproved_prefix_names(self):
        class_node, func_node_a, func_node_b, func_node_c, func_node_d, func_node_e, func_node_f, func_node_g, \
            func_node_h, func_node_i, func_node_j, func_node_k, func_node_l, func_node_m, func_node_n, func_node_o, \
            func_node_p = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace
            def build_configuration(self): #@
                pass
            def generate_thing(self): #@
                pass
            def make_thing(self): #@
                pass
            def insert_thing(self): #@
                pass
            def put_thing(self): #@
                pass
            def creates_configuration(self): #@
                pass
            def gets_thing(self): #@
                pass
            def lists_thing(self): #@
                pass
            def upserts_thing(self): #@
                pass
            def sets_thing(self): #@
                pass
            def updates_thing(self): #@
                pass
            def replaces_thing(self): #@
                pass
            def appends_thing(self): #@
                pass
            def adds_thing(self): #@
                pass
            def deletes_thing(self): #@
                pass
            def removes_thing(self): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_a
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_b
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_c
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_d
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_e
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_f
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_g
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_h
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_i
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_j
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_k
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_l
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_m
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_n
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_o
            ),
            pylint.testutils.Message(
                msg_id="unapproved-client-method-name-prefix", node=func_node_p
            )
        ):
            self.checker.visit_classdef(class_node)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#service-operations"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientConstructorTakesCorrectParameters(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientConstructorTakesCorrectParameters

    def test_finds_correct_params(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, thing_url, credential, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_non_constructor_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def create_configuration(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_non_client_constructor_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def __init__(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_without_kwargs(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, thing_url, credential=None): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-kwargs", node=function_node
            )
        ):
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_without_credentials(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, thing_url, **kwargs): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-credential", node=function_node
            )
        ):
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_with_no_params(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-credential", node=function_node
            ),
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-kwargs", node=function_node
            )
        ):
            self.checker.visit_functiondef(function_node)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#client-configuration"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientMethodsUseKwargsWithMultipleParameters(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientMethodsUseKwargsWithMultipleParameters

    def test_ignores_method_abiding_to_guidelines(self):
        class_node, function_node, function_node_a, function_node_b, function_node_c, function_node_d, \
            function_node_e, function_node_f, function_node_g, function_node_h, function_node_i, function_node_j, \
            function_node_k, function_node_l, function_node_m = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace
            def do_thing(): #@
                pass
            def do_thing_a(self): #@
                pass
            def do_thing_b(self, one): #@
                pass
            def do_thing_c(self, one, two): #@
                pass
            def do_thing_d(self, one, two, three): #@
                pass
            def do_thing_e(self, one, two, three, four): #@
                pass
            def do_thing_f(self, one, two, three, four, five): #@
                pass
            def do_thing_g(self, one, two, three, four, five, six=6): #@
                pass
            def do_thing_h(self, one, two, three, four, five, six=6, seven=7): #@
                pass
            def do_thing_i(self, one, two, three, four, five, *, six=6, seven=7): #@
                pass
            def do_thing_j(self, one, two, three, four, five, *, six=6, seven=7): #@
                pass
            def do_thing_k(self, one, two, three, four, five, **kwargs): #@
                pass
            def do_thing_l(self, one, two, three, four, five, *args, **kwargs): #@
                pass
            def do_thing_m(self, one, two, three, four, five, *args, six, seven=7, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)
            self.checker.visit_functiondef(function_node_c)
            self.checker.visit_functiondef(function_node_d)
            self.checker.visit_functiondef(function_node_e)
            self.checker.visit_functiondef(function_node_f)
            self.checker.visit_functiondef(function_node_g)
            self.checker.visit_functiondef(function_node_h)
            self.checker.visit_functiondef(function_node_i)
            self.checker.visit_functiondef(function_node_j)
            self.checker.visit_functiondef(function_node_k)
            self.checker.visit_functiondef(function_node_l)
            self.checker.visit_functiondef(function_node_m)

    def test_ignores_method_abiding_to_guidelines_async(self):
        class_node, function_node, function_node_a, function_node_b, function_node_c, function_node_d, \
            function_node_e, function_node_f, function_node_g, function_node_h, function_node_i, function_node_j, \
            function_node_k, function_node_l, function_node_m = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace_async
            async def do_thing(): #@
                pass
            async def do_thing_a(self): #@
                pass
            async def do_thing_b(self, one): #@
                pass
            async def do_thing_c(self, one, two): #@
                pass
            async def do_thing_d(self, one, two, three): #@
                pass
            async def do_thing_e(self, one, two, three, four): #@
                pass
            async def do_thing_f(self, one, two, three, four, five): #@
                pass
            async def do_thing_g(self, one, two, three, four, five, six=6): #@
                pass
            async def do_thing_h(self, one, two, three, four, five, six=6, seven=7): #@
                pass
            async def do_thing_i(self, one, two, three, four, five, *, six=6, seven=7): #@
                pass
            async def do_thing_j(self, one, two, three, four, five, *, six=6, seven=7): #@
                pass
            async def do_thing_k(self, one, two, three, four, five, **kwargs): #@
                pass
            async def do_thing_l(self, one, two, three, four, five, *args, **kwargs): #@
                pass
            async def do_thing_m(self, one, two, three, four, five, *args, six, seven=7, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node)
            self.checker.visit_asyncfunctiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)
            self.checker.visit_asyncfunctiondef(function_node_c)
            self.checker.visit_asyncfunctiondef(function_node_d)
            self.checker.visit_asyncfunctiondef(function_node_e)
            self.checker.visit_asyncfunctiondef(function_node_f)
            self.checker.visit_asyncfunctiondef(function_node_g)
            self.checker.visit_asyncfunctiondef(function_node_h)
            self.checker.visit_asyncfunctiondef(function_node_i)
            self.checker.visit_asyncfunctiondef(function_node_j)
            self.checker.visit_asyncfunctiondef(function_node_k)
            self.checker.visit_asyncfunctiondef(function_node_l)
            self.checker.visit_asyncfunctiondef(function_node_m)

    def test_finds_methods_with_too_many_positional_args(self):
        class_node, function_node, function_node_a, function_node_b, function_node_c, function_node_d, \
            function_node_e, function_node_f = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace
            def do_thing(self, one, two, three, four, five, six): #@
                pass
            def do_thing_a(self, one, two, three, four, five, six, seven=7): #@
                pass
            def do_thing_b(self, one, two, three, four, five, six, *, seven): #@
                pass
            def do_thing_c(self, one, two, three, four, five, six, *, seven, eight, nine): #@
                pass
            def do_thing_d(self, one, two, three, four, five, six, **kwargs): #@
                pass
            def do_thing_e(self, one, two, three, four, five, six, *args, seven, eight, nine): #@
                pass
            def do_thing_f(self, one, two, three, four, five, six, *args, seven=7, eight=8, nine=9): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_b
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_c
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_d
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_e
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_f
            )
        ):
            self.checker.visit_functiondef(function_node)
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)
            self.checker.visit_functiondef(function_node_c)
            self.checker.visit_functiondef(function_node_d)
            self.checker.visit_functiondef(function_node_e)
            self.checker.visit_functiondef(function_node_f)

    def test_finds_methods_with_too_many_positional_args_async(self):
        class_node, function_node, function_node_a, function_node_b, function_node_c, function_node_d, \
            function_node_e, function_node_f = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace_async
            async def do_thing(self, one, two, three, four, five, six): #@
                pass
            async def do_thing_a(self, one, two, three, four, five, six, seven=7): #@
                pass
            async def do_thing_b(self, one, two, three, four, five, six, *, seven): #@
                pass
            async def do_thing_c(self, one, two, three, four, five, six, *, seven, eight, nine): #@
                pass
            async def do_thing_d(self, one, two, three, four, five, six, **kwargs): #@
                pass
            async def do_thing_e(self, one, two, three, four, five, six, *args, seven, eight, nine): #@
                pass
            async def do_thing_f(self, one, two, three, four, five, six, *args, seven=7, eight=8, nine=9): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_b
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_c
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_d
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_e
            ),
            pylint.testutils.Message(
                msg_id="client-method-has-more-than-5-positional-arguments", node=function_node_f
            )
        ):
            self.checker.visit_asyncfunctiondef(function_node)
            self.checker.visit_asyncfunctiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)
            self.checker.visit_asyncfunctiondef(function_node_c)
            self.checker.visit_asyncfunctiondef(function_node_d)
            self.checker.visit_asyncfunctiondef(function_node_e)
            self.checker.visit_asyncfunctiondef(function_node_f)

    def test_ignores_non_client_methods(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomethingElse(): #@
            def do_thing(self, one, two, three, four, five, six): #@
                pass
            
            @distributed_trace_async
            async def do_thing(self, one, two, three, four, five, six): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_implementation.html#method-signatures"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientMethodsHaveTypeAnnotations(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientMethodsHaveTypeAnnotations

    def test_ignores_correct_type_annotations(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self, one: str, two: int, three: bool, four: Union[str, thing], five: dict) -> int: #@
                pass
            async def do_thing(self, one: str, two: int, three: bool, four: Union[str, thing], five: dict) -> int: #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)

    def test_ignores_correct_type_comments(self):
        class_node, function_node_a, function_node_b, function_node_c = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing_a(self, one, two, three, four, five): #@
                # type: (str, str, str, str, str) -> None
                pass

            def do_thing_b(self, one, two):  # type: (str, str) -> int #@
                pass

            def do_thing_c(self, #@
                           one,  # type: str
                           two,  # type: str
                           three,  # type: str
                           four,  # type: str
                           five  # type: str
                           ):
                # type: (...) -> int
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)
            self.checker.visit_functiondef(function_node_c)

    def test_ignores_correct_type_comments_async(self):
        class_node, function_node_a, function_node_b, function_node_c = astroid.extract_node("""
        class SomeClient(): #@
            async def do_thing_a(self, one, two, three, four, five): #@
                # type: (str, str, str, str, str) -> None
                pass

            async def do_thing_b(self, one, two):  # type: (str, str) -> int #@
                pass

            async def do_thing_c(self, #@
                           one,  # type: str
                           two,  # type: str
                           three,  # type: str
                           four,  # type: str
                           five  # type: str
                           ):
                # type: (...) -> int
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)
            self.checker.visit_asyncfunctiondef(function_node_c)

    def test_ignores_no_parameter_method_with_annotations(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing_a(self): #@
                # type: () -> None
                pass

            def do_thing_b(self) -> None: #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_ignores_no_parameter_method_with_annotations_async(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            async def do_thing_a(self): #@
                # type: () -> None
                pass

            async def do_thing_b(self) -> None: #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)

    def test_finds_no_parameter_method_without_annotations(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self): #@
                pass
            async def do_thing(self): #@
                pass
        """)

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-method-missing-type-annotations", node=function_node_a
                ),
                pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_b
                ),
        ):
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_method_missing_annotations(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self, one, two, three): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node
            )
        ):
            self.checker.visit_functiondef(function_node)

    def test_finds_method_missing_annotations_async(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            async def do_thing(self, one, two, three): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node
            )
        ):
            self.checker.visit_asyncfunctiondef(function_node)

    def test_finds_constructor_without_annotations(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, one, two, three, four, five): #@
                pass
        """)

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-method-missing-type-annotations", node=function_node
                )
        ):
            self.checker.visit_functiondef(function_node)

    def test_finds_missing_return_annotation_but_has_type_hints(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing_a(self, one: str, two: int, three: bool, four: Union[str, thing], five: dict): #@
                pass

            def do_thing_b(self, one, two, three, four, five): #@
                # type: (str, str, str, str, str)
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_b
            ),
        ):
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_missing_return_annotation_but_has_type_hints_async(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            async def do_thing_a(self, one: str, two: int, three: bool, four: Union[str, thing], five: dict): #@
                pass

            async def do_thing_b(self, one, two, three, four, five): #@
                # type: (str, str, str, str, str)
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_b
            ),
        ):
            self.checker.visit_asyncfunctiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)

    def test_finds_missing_annotations_but_has_return_hint(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing_a(self, one, two, three, four, five) -> None: #@
                pass

            def do_thing_b(self, one, two, three, four, five): #@
                # type: -> None
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_b
            )
        ):
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_missing_annotations_but_has_return_hint_async(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            async def do_thing_a(self, one, two, three, four, five) -> None: #@
                pass

            async def do_thing_b(self, one, two, three, four, five): #@
                # type: -> None
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-type-annotations", node=function_node_b
            )
        ):
            self.checker.visit_asyncfunctiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)

    def test_ignores_non_client_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def do_thing(self, one, two, three, four, five, six): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_private_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def _do_thing(self, one, two, three, four, five, six): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_implementation.html#types-or-not"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientHasKwargsInPoliciesForCreateConfigurationMethod(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientHasKwargsInPoliciesForCreateConfigurationMethod

    def test_ignores_config_policies_with_kwargs(self):
        function_node_a, function_node_b = astroid.extract_node("""
        def create_configuration(self, **kwargs): #@
            config = Configuration(**kwargs)
            config.headers_policy = StorageHeadersPolicy(**kwargs)
            config.user_agent_policy = StorageUserAgentPolicy(**kwargs)
            config.retry_policy = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
            config.redirect_policy = RedirectPolicy(**kwargs)
            config.logging_policy = StorageLoggingPolicy(**kwargs)
            config.proxy_policy = ProxyPolicy(**kwargs)
            return config

        @staticmethod
        def create_config(credential, api_version=None, **kwargs): #@
            # type: (TokenCredential, Optional[str], Mapping[str, Any]) -> Configuration
            if api_version is None:
                api_version = KeyVaultClient.DEFAULT_API_VERSION
            config = KeyVaultClient.get_configuration_class(api_version, aio=False)(credential, **kwargs)
            config.authentication_policy = ChallengeAuthPolicy(credential, **kwargs)
            return config
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_config_policies_without_kwargs(self):
        function_node_a, policy_a, policy_b, policy_c, function_node_b, policy_d = astroid.extract_node("""
        def create_configuration(self, **kwargs): #@
            config = Configuration(**kwargs)
            config.headers_policy = StorageHeadersPolicy(**kwargs)
            config.user_agent_policy = StorageUserAgentPolicy() #@
            config.retry_policy = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
            config.redirect_policy = RedirectPolicy(**kwargs)
            config.logging_policy = StorageLoggingPolicy() #@
            config.proxy_policy = ProxyPolicy() #@
            return config

        @staticmethod
        def create_config(credential, api_version=None, **kwargs): #@
            # type: (TokenCredential, Optional[str], Mapping[str, Any]) -> Configuration
            if api_version is None:
                api_version = KeyVaultClient.DEFAULT_API_VERSION
            config = KeyVaultClient.get_configuration_class(api_version, aio=False)(credential, **kwargs)
            config.authentication_policy = ChallengeAuthPolicy(credential) #@
            return config
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="config-missing-kwargs-in-policy", node=policy_a
            ),
            pylint.testutils.Message(
                msg_id="config-missing-kwargs-in-policy", node=policy_b
            ),
            pylint.testutils.Message(
                msg_id="config-missing-kwargs-in-policy", node=policy_c
            ),
            pylint.testutils.Message(
                msg_id="config-missing-kwargs-in-policy", node=policy_d
            )
        ):
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_ignores_policies_outside_create_config(self):
        function_node_a, function_node_b = astroid.extract_node("""
        def _configuration(self, **kwargs): #@
            config = Configuration(**kwargs)
            config.headers_policy = StorageHeadersPolicy(**kwargs)
            config.user_agent_policy = StorageUserAgentPolicy(**kwargs)
            config.retry_policy = kwargs.get('retry_policy') or ExponentialRetry()
            config.redirect_policy = RedirectPolicy()
            config.logging_policy = StorageLoggingPolicy()
            config.proxy_policy = ProxyPolicy()
            return config

        @staticmethod
        def some_other_method(credential, api_version=None, **kwargs): #@
            # type: (TokenCredential, Optional[str], Mapping[str, Any]) -> Configuration
            if api_version is None:
                api_version = KeyVaultClient.DEFAULT_API_VERSION
            config = KeyVaultClient.get_configuration_class(api_version, aio=False)(credential)
            config.authentication_policy = ChallengeAuthPolicy(credential)
            return config
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#client-configuration"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientUsesCorrectNamingConventions(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientUsesCorrectNamingConventions

    def test_ignores_constructor(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_internal_client(self):
        class_node, function_node = astroid.extract_node("""
        class _BaseSomeClient(): #@
            def __init__(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_private_method(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            def _private_method(self, **kwargs): #@
                pass
            async def _another_private_method(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_correct_client(self):
        class_node = astroid.extract_node("""
        class SomeClient(): #@
            pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_non_client(self):
        class_node, function_node = astroid.extract_node(
            """
        class SomethingElse(): #@
            def download_thing(self, some, **kwargs): #@
                pass
        """
        )

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_correct_method_names(self):
        class_node, function_node_a, function_node_b, function_node_c = astroid.extract_node("""
        class SomeClient(): #@
            def from_connection_string(self, **kwargs): #@
                pass
            def get_thing(self, **kwargs): #@
                pass
            def delete_thing(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_correct_method_names_async(self):
        class_node, function_node_a, function_node_b, function_node_c = astroid.extract_node("""
        class SomeClient(): #@
            def from_connection_string(self, **kwargs): #@
                pass
            def get_thing(self, **kwargs): #@
                pass
            def delete_thing(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_correct_class_constant(self):
        class_node = astroid.extract_node("""
        class SomeClient(): #@
            MAX_SIZE = 14
            MIN_SIZE = 2
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_finds_incorrectly_named_client(self):
        class_node_a, class_node_b, class_node_c = astroid.extract_node("""
        class some_client(): #@
            pass
        class Some_Client(): #@
            pass
        class someClient(): #@
            pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=class_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=class_node_b
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=class_node_c
            ),
        ):
            self.checker.visit_classdef(class_node_a)
            self.checker.visit_classdef(class_node_b)
            self.checker.visit_classdef(class_node_c)

    def test_finds_incorrectly_named_methods(self):
        class_node, func_node_a, func_node_b, func_node_c, func_node_d, func_node_e, func_node_f \
            = astroid.extract_node("""
        class SomeClient(): #@
            def Create_Config(self): #@
                pass
            def getThing(self): #@
                pass
            def List_thing(self): #@
                pass
            def UpsertThing(self): #@
                pass
            def set_Thing(self): #@
                pass
            def Updatething(self): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_b
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_c
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_d
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_e
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_f
            ),
        ):
            self.checker.visit_classdef(class_node)

    def test_finds_incorrectly_named_methods_async(self):
        class_node, func_node_a, func_node_b, func_node_c, func_node_d, func_node_e, func_node_f \
            = astroid.extract_node("""
        class SomeClient(): #@
            async def Create_Config(self): #@
                pass
            async def getThing(self): #@
                pass
            async def List_thing(self): #@
                pass
            async def UpsertThing(self): #@
                pass
            async def set_Thing(self): #@
                pass
            async def Updatething(self): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_b
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_c
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_d
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_e
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=func_node_f
            ),
        ):
            self.checker.visit_classdef(class_node)

    def test_finds_incorrectly_named_class_constant(self):
        class_node, const_a, const_b = astroid.extract_node("""
        class SomeClient(): #@
            max_size = 14 #@
            min_size = 2 #@
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=const_a
            ),
            pylint.testutils.Message(
                msg_id="client-incorrect-naming-convention", node=const_b
            ),
        ):
            self.checker.visit_classdef(class_node)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_implementation.html#naming-conventions"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientMethodsHaveKwargsParameter(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientMethodsHaveKwargsParameter

    def test_ignores_private_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def _create_configuration(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_properties(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            @property
            def key_id(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_properties_async(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            @property
            async def key_id(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node)

    def test_ignores_non_client_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def create_configuration(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_methods_with_kwargs(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            def get_thing(self, **kwargs): #@
                pass
            @distributed_trace
            def remove_thing(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_missing_kwargs(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        from azure.core.tracing.decorator import distributed_trace
        
        class SomeClient(): #@
            @distributed_trace
            def get_thing(self): #@
                pass
            @distributed_trace
            def remove_thing(self): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-kwargs", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-kwargs", node=function_node_b
            ),
        ):
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_ignores_methods_with_kwargs_async(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            async def get_thing(self, **kwargs): #@
                pass
            async def remove_thing(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)

    def test_finds_missing_kwargs_async(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        from azure.core.tracing.decorator_async import distributed_trace_async
        
        class SomeClient(): #@
            @distributed_trace_async
            async def get_thing(self): #@
                pass
            @distributed_trace_async
            async def remove_thing(self): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-method-missing-kwargs", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-method-missing-kwargs", node=function_node_b
            ),
        ):
            self.checker.visit_asyncfunctiondef(function_node_a)
            self.checker.visit_asyncfunctiondef(function_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#constructors-and-factory-methods"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestAsyncClientCorrectNaming(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.AsyncClientCorrectNaming

    def test_ignores_private_client(self):
        class_node = astroid.extract_node("""
        class _AsyncBaseSomeClient(): #@
            def create_configuration(self):
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_correct_client(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def create_configuration(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_async_base_named_client(self):
        class_node_a = astroid.extract_node("""
        class AsyncSomeClientBase(): #@
            def get_thing(self, **kwargs):
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node_a)

    def test_finds_incorrectly_named_client(self):
        class_node_a = astroid.extract_node("""
        class AsyncSomeClient(): #@
            def get_thing(self, **kwargs):
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="async-client-bad-name", node=class_node_a
            ),
        ):
            self.checker.visit_classdef(class_node_a)

    def test_ignores_non_client(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def create_configuration(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#async-support"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestFileHasCopyrightHeader(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.FileHasCopyrightHeader

    def test_copyright_header_acceptable(self):
        file = open("./test_files/copyright_header_acceptable.py")
        node = astroid.parse(file.read())
        file.close()

        with self.assertNoMessages():
            self.checker.visit_module(node)

    def test_copyright_header_violation(self):
        file = open("./test_files/copyright_header_violation.py")
        node = astroid.parse(file.read())
        file.close()

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="file-needs-copyright-header", node=node
                )
        ):
            self.checker.visit_module(node)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/policies_opensource.html"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestSpecifyParameterNamesInCall(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.SpecifyParameterNamesInCall

    def test_ignores_call_with_only_two_unnamed_params(self):
        class_node, call_node = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self):
                self._client.thing(one, two) #@
        """)

        with self.assertNoMessages():
            self.checker.visit_call(call_node)

    def test_ignores_call_with_two_unnamed_params_and_one_named(self):
        class_node, call_node = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self):
                self._client.thing(one, two, three=3) #@
        """)

        with self.assertNoMessages():
            self.checker.visit_call(call_node)

    def test_ignores_call_from_non_client(self):
        class_node, call_node = astroid.extract_node("""
        class SomethingElse(): #@
            def do_thing(self):
                self._other.thing(one, two, three) #@
        """)

        with self.assertNoMessages():
            self.checker.visit_call(call_node)

    def test_ignores_call_with_named_params(self):
        class_node, call_node_a, call_node_b, call_node_c = astroid.extract_node("""
        class SomethingElse(): #@
            def do_thing_a(self):
                self._other.thing(one=one, two=two, three=three) #@
            def do_thing_b(self):
                self._other.thing(zero, number, one=one, two=two, three=three) #@
            def do_thing_c(self):
                self._other.thing(zero, one=one, two=two, three=three) #@      
        """)

        with self.assertNoMessages():
            self.checker.visit_call(call_node_a)
            self.checker.visit_call(call_node_b)
            self.checker.visit_call(call_node_c)

    def test_ignores_non_client_function_call(self):
        call_node = astroid.extract_node("""
        def do_thing():
            self._client.thing(one, two, three) #@
        """)

        with self.assertNoMessages():
            self.checker.visit_call(call_node)

    def test_finds_call_with_more_than_two_unnamed_params(self):
        class_node, call_node = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self):
                self._client.thing(one, two, three) #@
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="specify-parameter-names-in-call", node=call_node
            ),
        ):
            self.checker.visit_call(call_node)

    def test_finds_call_with_more_than_two_unnamed_params_and_some_named(self):
        class_node, call_node = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self):
                self._client.thing(one, two, three, four=4, five=5) #@
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="specify-parameter-names-in-call", node=call_node
            ),
        ):
            self.checker.visit_call(call_node)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_implementation.html#python-codestyle-positional-params"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientListMethodsUseCorePaging(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientListMethodsUseCorePaging

    def test_ignores_private_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def _list_thing(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_non_client_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def list_things(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_methods_return_ItemPaged(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        from azure.core.paging import ItemPaged
        
        class SomeClient(): #@
            def list_thing(self): #@
                return ItemPaged()
            @distributed_trace
            def list_thing2(self): #@
                return ItemPaged(
                    command, prefix=name_starts_with, results_per_page=results_per_page,
                    page_iterator_class=BlobPropertiesPaged)
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_ignores_methods_return_AsyncItemPaged(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        from azure.core.async_paging import AsyncItemPaged
        
        class SomeClient(): #@
            async def list_thing(self): #@
                return AsyncItemPaged()
            @distributed_trace
            def list_thing2(self): #@
                return AsyncItemPaged(
                    command, prefix=name_starts_with, results_per_page=results_per_page,
                    page_iterator_class=BlobPropertiesPaged)
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_method_returning_something_else(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        from azure.core.polling import LROPoller
        
        class SomeClient(): #@
            def list_thing(self): #@
                return list()
            def list_thing2(self): #@
                return LROPoller()
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-list-methods-use-paging", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-list-methods-use-paging", node=function_node_b
            ),
        ):
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_method_returning_something_else_async(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        from azure.core.polling import LROPoller
        
        class SomeClient(): #@
            async def list_thing(self, **kwargs): #@
                return list()
            async def list_thing2(self, **kwargs): #@
                from azure.core.polling import LROPoller
                return LROPoller()
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-list-methods-use-paging", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-list-methods-use-paging", node=function_node_b
            ),
        ):
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#response-formats"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientLROMethodsUseCorePolling(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientLROMethodsUseCorePolling

    def test_ignores_private_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def _begin_thing(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_non_client_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def begin_things(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_methods_return_LROPoller(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        from azure.core.polling import LROPoller
        
        class SomeClient(): #@
            def begin_thing(self): #@
                return LROPoller()
            @distributed_trace
            def begin_thing2(self): #@
                return LROPoller(self._client, raw_result, get_long_running_output, polling_method)
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_method_returning_something_else(self):
        class_node, function_node_a, function_node_b = astroid.extract_node("""
        class SomeClient(): #@
            def begin_thing(self): #@
                return list()
            def begin_thing2(self): #@
                return {}
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="client-lro-methods-use-polling", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="client-lro-methods-use-polling", node=function_node_b
            ),
        ):
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#response-formats"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientLROMethodsUseCorrectNaming(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientLROMethodsUseCorrectNaming

    def test_ignores_private_methods(self):
        class_node, return_node = astroid.extract_node("""
        from azure.core.polling import LROPoller
        
        class SomeClient(): #@
            def _do_thing(self): 
                return LROPoller(self._client, raw_result, get_long_running_output, polling_method) #@
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_return(return_node)

    def test_ignores_non_client_methods(self):
        class_node, return_node = astroid.extract_node("""
        from azure.core.polling import LROPoller
        
        class SomethingElse(): #@
            def begin_things(self):
                return LROPoller(self._client, raw_result, get_long_running_output, polling_method) #@
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_return(return_node)

    def test_ignores_methods_return_LROPoller_and_correctly_named(self):
        class_node, return_node_a, return_node_b = astroid.extract_node("""
        from azure.core.polling import LROPoller
        
        class SomeClient(): #@
            def begin_thing(self):
                return LROPoller() #@
            @distributed_trace
            def begin_thing2(self):
                return LROPoller(self._client, raw_result, get_long_running_output, polling_method) #@
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_return(return_node_a)
            self.checker.visit_return(return_node_b)

    def test_finds_incorrectly_named_method_returning_LROPoller(self):
        class_node, function_node_a, return_node_a, function_node_b, return_node_b = astroid.extract_node("""
        from azure.core.polling import LROPoller
        
        class SomeClient(): #@
            def poller_thing(self): #@
                return LROPoller() #@
            @distributed_trace
            def start_thing2(self): #@
                return LROPoller(self._client, raw_result, get_long_running_output, polling_method) #@
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="lro-methods-use-correct-naming", node=function_node_a
            ),
            pylint.testutils.Message(
                msg_id="lro-methods-use-correct-naming", node=function_node_b
            ),
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_return(return_node_a)
            self.checker.visit_return(return_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#service-operations"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientConstructorDoesNotHaveConnectionStringParam(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientConstructorDoesNotHaveConnectionStringParam

    def test_ignores_client_with_no_conn_str_in_constructor(self):
        class_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self): 
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_non_client_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def __init__(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_finds_client_method_using_conn_str_in_constructor_a(self):
        class_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, connection_string):
                return list()
        """)

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="connection-string-should-not-be-constructor-param", node=class_node
                ),
        ):
            self.checker.visit_classdef(class_node)

    def test_finds_client_method_using_conn_str_in_constructor_b(self):
        class_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, conn_str):
                return list()
        """)

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="connection-string-should-not-be-constructor-param", node=class_node
                ),
        ):
            self.checker.visit_classdef(class_node)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#python-client-connection-string"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200

class TestPackageNameDoesNotUseUnderscoreOrPeriod(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.PackageNameDoesNotUseUnderscoreOrPeriod

    def test_package_name_acceptable(self):

        package_name =  astroid.extract_node(
        """
        PACKAGE_NAME = "correct-package-name"        
        """ 
        )
        module_node = astroid.Module(name = "node", file="setup.py", doc = """ """)
        module_node.body = [package_name]

        with self.assertNoMessages():
            self.checker.visit_module(module_node)

    def test_package_name_violation(self):

        package_name =  astroid.extract_node(
        """
        PACKAGE_NAME = "incorrect.package-name"        
        """ 
        )
        module_node = astroid.Module(name = "node", file="setup.py", doc = """ """)
        module_node.body = [package_name]

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="package-name-incorrect", node=module_node
                )
        ):
            self.checker.visit_module(module_node)
    
    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#packaging"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200

class TestServiceClientUsesNameWithClientSuffix(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ServiceClientUsesNameWithClientSuffix

    def test_client_suffix_acceptable(self):
        client_node =  astroid.extract_node(
        """
        class MyClient():
            def __init__(self):
                pass       
        """ 
        )
        module_node = astroid.Module(name = "node", file="_my_client.py", doc = """ """)
        module_node.body = [client_node]

        with self.assertNoMessages():
            self.checker.visit_module(module_node)
    
    def test_client_suffix_violation(self):
        client_node =  astroid.extract_node(
        """
        class Violation():
            def __init__(self):
                pass       
        """ 
        )
        module_node = astroid.Module(name = "node", file="_my_client.py", doc = """ """)
        module_node.body = [client_node]
        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-suffix-needed", node=module_node
                )
        ):
            self.checker.visit_module(module_node)
    
    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#service-client"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientMethodNamesDoNotUseDoubleUnderscorePrefix(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientMethodNamesDoNotUseDoubleUnderscorePrefix

    def test_ignores_repr(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __repr__(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_constructor(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_other_dunder(self):
        class_node, function_node_a, function_node_b, function_node_c, function_node_d = astroid.extract_node("""
        class SomeClient(): #@
            def __enter__(self): #@
                pass
            def __exit__(self): #@
                pass
            def __aenter__(self): #@
                pass
            def __aexit__(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)
            self.checker.visit_functiondef(function_node_c)
            self.checker.visit_functiondef(function_node_d)

    def test_ignores_private_method(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            @staticmethod
            def _private_method(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_private_method_async(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            @staticmethod
            async def _private_method(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node)

    def test_ignores_methods_with_decorators(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace
            def create_configuration(self): #@
                pass
            @distributed_trace
            def get_thing(self): #@
                pass
            @distributed_trace
            def list_thing(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_functiondef(func_node_b)
            self.checker.visit_functiondef(func_node_c)

    def test_ignores_async_methods_with_decorators(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        class SomeClient(): #@
            @distributed_trace_async
            async def create_configuration(self): #@
                pass
            @distributed_trace_async
            async def get_thing(self): #@
                pass
            @distributed_trace_async
            async def list_thing(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)
            self.checker.visit_asyncfunctiondef(func_node_c)

    def test_finds_double_underscore_on_async_method(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        class SomeClient(): #@
            @staticmethod
            async def __create_configuration(self): #@
                pass
            @staticmethod
            async def __get_thing(self): #@
                pass
            @staticmethod
            async def __list_thing(self): #@
                pass
        """)
        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-method-name-no-double-underscore", node=func_node_a
                ),
                pylint.testutils.Message(
                    msg_id="client-method-name-no-double-underscore", node=func_node_b
                ),
                pylint.testutils.Message(
                    msg_id="client-method-name-no-double-underscore", node=func_node_c
                ),
        ):
            self.checker.visit_asyncfunctiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)
            self.checker.visit_asyncfunctiondef(func_node_c)

    def test_finds_double_underscore_on_sync_method(self):
        class_node, func_node_a, func_node_b, func_node_c = astroid.extract_node("""
        class SomeClient(): #@
            @staticmethod
            def __create_configuration(self): #@
                pass
            @staticmethod
            def __get_thing(self): #@
                pass
            @staticmethod
            def __list_thing(self): #@
                pass
        """)
        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-method-name-no-double-underscore", node=func_node_a
                ),
                pylint.testutils.Message(
                    msg_id="client-method-name-no-double-underscore", node=func_node_b
                ),
                pylint.testutils.Message(
                    msg_id="client-method-name-no-double-underscore", node=func_node_c
                ),
        ):
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_functiondef(func_node_b)
            self.checker.visit_functiondef(func_node_c)

    def test_ignores_non_client_method(self):
        class_node, func_node_a, func_node_b = astroid.extract_node(
            """
        class SomethingElse(): #@
            @staticmethod
            def __download_thing(self, some, **kwargs): #@
                pass

            @staticmethod
            async def __do_thing(self, some, **kwargs): #@
                pass
        """
        )
        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node_a)
            self.checker.visit_asyncfunctiondef(func_node_b)

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_implementation.html#public-vs-private"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200

class TestCheckDocstringAdmonitionNewline(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.CheckDocstringAdmonitionNewline

    def test_ignores_correct_admonition_statement_in_function(self):
        function_node = astroid.extract_node(
            """
            def function_foo(x, y, z):
                '''docstring
                .. admonition:: Example:

                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
            """
        )

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_ignores_correct_admonition_statement_in_function_with_comments(self):
        function_node = astroid.extract_node(
            """
            def function_foo(x, y, z):
                '''docstring
                .. admonition:: Example:
                    This is Example content.
                    Should support multi-line.
                    Can also include file:

                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
            """
        )

        with self.assertNoMessages():
            self.checker.visit_functiondef(function_node)

    def test_bad_admonition_statement_in_function(self):
        function_node = astroid.extract_node(
            """
            def function_foo(x, y, z):
                '''docstring
                .. admonition:: Example:
                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
            """
        )

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="docstring-admonition-needs-newline", node=function_node
                )
        ):
            self.checker.visit_functiondef(function_node)

    def test_bad_admonition_statement_in_function_with_comments(self):
        function_node = astroid.extract_node(
            """
            def function_foo(x, y, z):
                '''docstring
                .. admonition:: Example:
                    This is Example content.
                    Should support multi-line.
                    Can also include file:
                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
            """
        )

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="docstring-admonition-needs-newline", node=function_node
                )
        ):
            self.checker.visit_functiondef(function_node)

    def test_ignores_correct_admonition_statement_in_function_async(self):
        function_node = astroid.extract_node(
            """
            async def function_foo(x, y, z):
                '''docstring
                .. admonition:: Example:

                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
            """
        )

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node)

    def test_ignores_correct_admonition_statement_in_function_with_comments_async(self):
        function_node = astroid.extract_node(
            """
            async def function_foo(x, y, z):
                '''docstring
                .. admonition:: Example:
                    This is Example content.
                    Should support multi-line.
                    Can also include file:

                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
            """
        )

        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(function_node)

    def test_bad_admonition_statement_in_function_async(self):
        function_node = astroid.extract_node(
            """
            async def function_foo(x, y, z):
                '''docstring
                .. admonition:: Example:
                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
            """
        )

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="docstring-admonition-needs-newline", node=function_node
                )
        ):
            self.checker.visit_asyncfunctiondef(function_node)

    def test_bad_admonition_statement_in_function_with_comments_async(self):
        function_node = astroid.extract_node(
            """
            async def function_foo(x, y, z):
                '''docstring
                .. admonition:: Example:
                    This is Example content.
                    Should support multi-line.
                    Can also include file:
                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
            """
        )

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="docstring-admonition-needs-newline", node=function_node
                )
        ):
            self.checker.visit_asyncfunctiondef(function_node)

    def test_ignores_correct_admonition_statement_in_class(self):
        class_node = astroid.extract_node(
            """
            class SomeClient(object):
                '''docstring
                .. admonition:: Example:

                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
                def __init__(self):
                    pass
            """
        )

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_correct_admonition_statement_in_class_with_comments(self):
        class_node = astroid.extract_node(
            """
            class SomeClient(object):
                '''docstring
                .. admonition:: Example:
                    This is Example content.
                    Should support multi-line.
                    Can also include file:

                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
                def __init__(self):
                    pass
            """
        )

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_bad_admonition_statement_in_class(self):
        class_node = astroid.extract_node(
            """
            class SomeClient(object):
                '''docstring
                .. admonition:: Example:
                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
                def __init__(self):
                    pass
            """
        )

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="docstring-admonition-needs-newline", node=class_node
                )
        ):
            self.checker.visit_classdef(class_node)

    def test_bad_admonition_statement_in_class_with_comments(self):
        class_node = astroid.extract_node(
            """
            class SomeClient(object):
                '''docstring
                .. admonition:: Example:
                    This is Example content.
                    Should support multi-line.
                    Can also include file:
                    .. literalinclude:: ../samples/sample_detect_language.py
                '''
                def __init__(self):
                    pass
            """
        )

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="docstring-admonition-needs-newline", node=class_node
                )
        ):
            self.checker.visit_classdef(class_node)        
    
    
class TestCheckNamingMismatchGeneratedCode(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.CheckNamingMismatchGeneratedCode

    def test_import_naming_mismatch_violation(self):
        import_one = astroid.extract_node(
            'import Something'
           
        )
        import_two =  astroid.extract_node(
            'import Something2 as SomethingTwo'
           
        )
        assign_one = astroid.extract_node(
        """
            __all__ =(
            "Something",
            "SomethingTwo", 
            ) 
          """
        )
      
        module_node = astroid.Module(name = "node", file="__init__.py", doc = """ """)
        module_node.body = [import_one,import_two,assign_one]

        for name in module_node.body[-1].assigned_stmts():
            err_node = name.elts[1]
     
        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="naming-mismatch", node=err_node ,confidence=None
                )
        ):
            self.checker.visit_module(module_node)

    def test_import_from_naming_mismatch_violation(self):
        import_one = astroid.extract_node(
            'import Something'
           
        )
        import_two =  astroid.extract_node(
            'from Something2 import SomethingToo as SomethingTwo'
           
        )
        assign_one = astroid.extract_node(
        """
            __all__ =(
            "Something",
            "SomethingTwo", 
            ) 
          """
        )
      
        module_node = astroid.Module(name = "node", file="__init__.py", doc = """ """)
        module_node.body = [import_one,import_two,assign_one]

        for name in module_node.body[-1].assigned_stmts():
            err_node = name.elts[1]
     
        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="naming-mismatch", node=err_node ,confidence=None
                )
        ):
            self.checker.visit_module(module_node)

    def test_naming_mismatch_acceptable(self):
        import_one = astroid.extract_node(
            'import Something'
           
        )
        import_two =  astroid.extract_node(
            'import Something2 as SomethingTwo'
           
        )
        assign_one = astroid.extract_node(
        """
            __all__ =(
            "Something",
            "Something2", 
            ) 
          """
        )
      
        module_node = astroid.Module(name = "node", file="__init__.py", doc = """ """)
        module_node.body = [import_one,import_two,assign_one]

        with self.assertNoMessages():
            self.checker.visit_module(module_node)
    
    def test_naming_mismatch_pylint_disable(self):

        file = open("./test_files/__init__.py")
        node = astroid.parse(file.read())
        file.close()

        with self.assertNoMessages():
            self.checker.visit_module(node)

    def test_guidelines_link_active(self):
        url = "https://github.com/Azure/autorest/blob/main/docs/generate/built-in-directives.md"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200

class TestCheckEnum(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.CheckEnum

    def test_ignore_normal_class(self):
        class_node = astroid.extract_node(
            """
               class SomeClient(object):
                    my_list = []
            """
        )

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_enum_capitalized_violation_python_two(self):
        class_node = astroid.extract_node(
            """
            from enum import Enum
            from six import with_metaclass
            from azure.core import CaseInsensitiveEnumMeta

            class MyBadEnum(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)): 
                One = "one"
              """
        )

        with self.assertAddsMessages(
             pylint.testutils.Message(
                msg_id="enum-must-be-uppercase", node=class_node.body[0].targets[0]
            )
        ):
            self.checker.visit_classdef(class_node)
    
    def test_enum_capitalized_violation_python_three(self):
        class_node = astroid.extract_node(
            """
            from enum import Enum
            from azure.core import CaseInsensitiveEnumMeta

            class MyBadEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta): 
                One = "one"
            
            """
        )
 
        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="enum-must-be-uppercase", node=class_node.body[0].targets[0]
            )
        ):
            self.checker.visit_classdef(class_node)
    
    def test_inheriting_case_insensitive_violation(self):
        class_node = astroid.extract_node(
            """
            from enum import Enum

            class MyGoodEnum(str, Enum): 
                ONE = "one"
            """
        )

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="enum-must-inherit-case-insensitive-enum-meta", node=class_node )
        ):
            self.checker.visit_classdef(class_node)

    def test_acceptable_python_three(self):
        class_node = astroid.extract_node(
            """
            from enum import Enum
            from azure.core import CaseInsensitiveEnumMeta

            class MyGoodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta): 
                ONE = "one"
            """
        )         

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)   

    def test_enum_file_acceptable_python_two(self):
        file = open("./test_files/enum_checker_acceptable.py")
        node = astroid.parse(file.read())
        file.close()
        
        with self.assertNoMessages():
            self.checker.visit_classdef(node.body[3])        
    
    def test_enum_file_both_violation(self):
        file = open("./test_files/enum_checker_violation.py")
        node = astroid.parse(file.read())
        file.close()

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="enum-must-inherit-case-insensitive-enum-meta", node=node.body[1]
            ),
            pylint.testutils.Message(
                msg_id="enum-must-be-uppercase", node=node.body[1].body[0].targets[0]
            )
        ):

            self.checker.visit_classdef(node.body[1])

    def test_guidelines_link_active(self):
        self._create_url_pipeline("https://azure.github.io/azure-sdk/python_design.html#enumerations")
        self._create_url_pipeline("https://azure.github.io/azure-sdk/python_implementation.html#extensible-enumerations")
        
    
    def _create_url_pipeline(self,url):
        resp = requests.get(url)
        assert resp.status_code == 200
        
        
            
class TestCheckAPIVersion(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.CheckAPIVersion

    def test_api_version_violation(self):
        class_node = astroid.extract_node(
            """
            class SomeClient(object):
                '''
                   :param str something: something
                '''
                def __init__(self, something, **kwargs):
                    pass
            """
        )

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-accepts-api-version-keyword", node=class_node
                )
        ):
            self.checker.visit_classdef(class_node)

    def test_api_version_acceptable(self):
        class_node = astroid.extract_node(
            """
            class SomeClient(object):
                '''
                   :param str something: something 
                   :keyword str api_version: api_version
                '''
                def __init__(self, something, **kwargs):
                    pass
            """
        )
    
        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
    
    def test_api_version_file_class_acceptable(self):
        file = open("./test_files/api_version_checker_acceptable_class.py")
        node = astroid.parse(file.read())
        file.close()
    
        with self.assertNoMessages():
            self.checker.visit_classdef(node.body[0])

    def test_api_version_file_init_acceptable(self):
        file = open("./test_files/api_version_checker_acceptable_init.py")
        node = astroid.parse(file.read())
        file.close()

        with self.assertNoMessages():
            self.checker.visit_classdef(node.body[0])


    def test_api_version_file_violation(self):
        file = open("./test_files/api_version_checker_violation.py")
        node = astroid.parse(file.read())
        file.close()

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-accepts-api-version-keyword", node=node.body[0]
                )
        ):
            self.checker.visit_classdef(node.body[0])

    def test_guidelines_link_active(self):
        url = "https://azure.github.io/azure-sdk/python_design.html#specifying-the-service-version"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200
