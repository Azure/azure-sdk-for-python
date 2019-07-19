import astroid
import pylint.testutils

from azure.core import PipelineClient, Configuration
from plugins import pylint_guidelines_checker as checker


class TestClientHasConfigurationMethod(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientHasCreateConfigurationMethod

    def test_missing_create_config_method(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, **kwargs): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-configuration-factory-method", node=class_node
            )
        ):
            self.checker.visit_classdef(class_node)

    def test_finds_config_method(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def create_configuration(self, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_finds_config_method_without_kwargs(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def create_configuration(self): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-configuration-factory-method-kwargs", node=function_node
            )
        ):
            self.checker.visit_classdef(class_node)

    def test_ignores_non_client_missing_config_method(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def __init__(self, some, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_ignores_nested_function_missing_create_config(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def create_configuration(self, **kwargs): #@
                def nested(hello, world):
                    pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)

    def test_guidelines_link_active(self):
        url = "https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-constructorsfactory-methods"
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
        url = "https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-constructorsfactory-methods"
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
            def __init__(self, thing_url, credentials, transport, **kwargs): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_ignores_non_constructor_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def create_configuration(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_ignores_non_client_constructor_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def __init__(self): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_without_kwargs(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, thing_url, credentials=None, transport=None): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-kwargs", node=function_node
            )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_without_credentials(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, thing_url, transport, **kwargs): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-credentials", node=function_node
            )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_without_transport(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, thing_url, credentials, **kwargs): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-transport", node=function_node
            )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_with_no_params(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-credentials", node=function_node
            ),
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-transport", node=function_node
            ),
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-kwargs", node=function_node
            )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_missing_two_params_a(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, transport): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-credentials", node=function_node
            ),
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-kwargs", node=function_node
            )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_missing_two_params_b(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, credentials): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-transport", node=function_node
            ),
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-kwargs", node=function_node
            )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_finds_constructor_missing_two_params_c(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def __init__(self, **kwargs): #@
                pass
        """)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-credentials", node=function_node
            ),
            pylint.testutils.Message(
                msg_id="missing-client-constructor-parameter-transport", node=function_node
            )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_guidelines_link_active(self):
        url = "https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-constructorsfactory-methods"
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
            self.checker.visit_classdef(class_node)
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

    def test_finds_methods_with_too_many_positional_args(self):
        class_node, function_node, function_node_a, function_node_b, function_node_c, function_node_d, \
            function_node_e, function_node_f = astroid.extract_node("""
        class SomeClient(): #@
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
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)
            self.checker.visit_functiondef(function_node_c)
            self.checker.visit_functiondef(function_node_d)
            self.checker.visit_functiondef(function_node_e)
            self.checker.visit_functiondef(function_node_f)

    def test_ignores_non_client_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def do_thing(self, one, two, three, four, five, six): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_guidelines_link_active(self):
        url = "https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#sec-method-signatures"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200


class TestClientMethodsHaveTypeAnnotations(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.ClientMethodsHaveTypeAnnotations

    def test_ignores_correct_type_annotations(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self, one: str, two: int, three: bool, four: Union[str, thing], five: dict) -> int: #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

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
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)
            self.checker.visit_functiondef(function_node_c)

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
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_finds_no_parameter_method_without_annotations(self):
        class_node, function_node = astroid.extract_node("""
        class SomeClient(): #@
            def do_thing(self): #@
                pass
        """)

        with self.assertAddsMessages(
                pylint.testutils.Message(
                    msg_id="client-method-missing-type-annotations", node=function_node
                )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

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
            self.checker.visit_classdef(class_node)
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
            )
        ):
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

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
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node_a)
            self.checker.visit_functiondef(function_node_b)

    def test_ignores_non_client_methods(self):
        class_node, function_node = astroid.extract_node("""
        class SomethingElse(): #@
            def do_thing(self, one, two, three, four, five, six): #@
                pass
        """)

        with self.assertNoMessages():
            self.checker.visit_classdef(class_node)
            self.checker.visit_functiondef(function_node)

    def test_guidelines_link_active(self):
        url = "https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html#python-type-hints"
        config = Configuration()
        client = PipelineClient(url, config=config)
        request = client.get(url)
        response = client._pipeline.run(request)
        assert response.http_response.status_code == 200
