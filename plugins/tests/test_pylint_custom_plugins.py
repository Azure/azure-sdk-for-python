import astroid
import pylint.testutils

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
            def __init__(self, thing_url, credentials, transport): #@
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