#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import json
import sys
import pytest

PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.dirname(PACKAGE_DIR)

for path in (SCRIPTS_DIR, PACKAGE_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from breaking_changes_checker.checkers.added_method_overloads_checker import AddedMethodOverloadChecker
from breaking_changes_checker.changelog_tracker import ChangelogTracker, BreakingChangesTracker
from breaking_changes_checker.detect_breaking_changes import main
from breaking_changes_checker.detect_breaking_changes import compare_report_dicts, drop_shadow_types_modules, get_property_names
from breaking_changes_checker.detect_breaking_changes import test_compare_reports as compare_reports


def test_changelog_flag():
    with open(os.path.join(os.path.dirname(__file__), "examples", "code-reports", "content-safety", "stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "examples", "code-reports", "content-safety", "current.json"), "r") as fd:
        current = json.load(fd)

    bc = ChangelogTracker(stable, current, "azure-ai-contentsafety")
    bc.run_checks()

    assert len(bc.features_added) > 0
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLIENT_METHOD_MSG
    assert args == ['azure.ai.contentsafety', 'BlocklistClient', 'new_blocklist_client_method']

def test_new_class_property_added():
    # Testing reporting on class level property added
    current = {
        "azure.ai.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                        "new_class_att": "str"
                    }
                },
            }
        }
    }

    stable = {
        "azure.ai.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                    }
                },
            }
        }
    }

    bc = ChangelogTracker(stable, current, "azure-ai-contentsafety")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_PROPERTY_MSG
    assert args == ['azure.ai.contentsafety', 'AnalyzeTextResult', 'new_class_att']


def test_async_cleanup_check():
    stable = {
        "azure.mgmt.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                        "new_class_att": "str"
                    }
                },
            }
        },
        "azure.mgmt.aio.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                        "new_class_att": "str"
                    }
                },
            }
        }
    }

    current = {
        "azure.mgmt.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                        "new_property": "str"
                    }
                },
            }
        },
        "azure.mgmt.aio.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                        "new_property": "str"
                    }
                },
            }
        }
    }

    bc = ChangelogTracker(stable, current, "azure-mgmt-contentsafety")
    bc.run_checks()

    # Should only have 1 breaking change reported instead of 2
    assert len(bc.breaking_changes) == 1
    msg, _, *args = bc.breaking_changes[0]
    assert msg == BreakingChangesTracker.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_MODEL_MSG
    # Should only have 1 feature added reported instead of 2
    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_PROPERTY_MSG


def test_drop_shadow_types_modules_removes_generated_types():
    # A generated `types` module is a projection of the sibling `models` module and is dropped
    # from both reports before diffing.
    stable = {
        "azure.mgmt.computelimit.models": {"class_nodes": {}},
        "azure.mgmt.computelimit.types": {"class_nodes": {}},
    }
    current = {
        "azure.mgmt.computelimit.models": {"class_nodes": {}},
        "azure.mgmt.computelimit.types": {"class_nodes": {}},
    }

    stable_out, current_out = drop_shadow_types_modules(stable, current)

    assert set(stable_out) == {"azure.mgmt.computelimit.models"}
    assert set(current_out) == {"azure.mgmt.computelimit.models"}


def test_drop_shadow_types_modules_is_symmetric():
    # The module is dropped from both sides even when it only exists on one of them, otherwise
    # the diff would report a phantom added/removed module.
    stable = {
        "azure.mgmt.computelimit.models": {"class_nodes": {}},
        "azure.mgmt.computelimit.types": {"class_nodes": {}},
    }
    current = {
        "azure.mgmt.computelimit.models": {"class_nodes": {}},
    }

    stable_out, current_out = drop_shadow_types_modules(stable, current)

    assert set(stable_out) == {"azure.mgmt.computelimit.models"}
    assert set(current_out) == {"azure.mgmt.computelimit.models"}


def test_drop_shadow_types_modules_keeps_types_without_models_sibling():
    # Without a sibling `models` module, a `types` module is a real hand-written public module
    # and must keep being checked.
    stable = {"azure.mgmt.computelimit.types": {"class_nodes": {}}}
    current = {"azure.mgmt.computelimit.types": {"class_nodes": {}}}

    stable_out, current_out = drop_shadow_types_modules(stable, current)

    assert set(stable_out) == {"azure.mgmt.computelimit.types"}
    assert set(current_out) == {"azure.mgmt.computelimit.types"}


def test_drop_shadow_types_modules_keeps_types_owning_a_class():
    # The guard is a subset relation, not just a name check: a `types` module that declares a
    # class with no counterpart in the sibling `models` module is not a pure projection, so it
    # is kept and diffed normally. This covers a package that hand-writes both modules.
    node = {"type": None, "methods": {}, "properties": {}}
    stable = {
        "azure.mgmt.computelimit.models": {"class_nodes": {"SharedModel": node}},
        "azure.mgmt.computelimit.types": {"class_nodes": {"SharedModel": node, "OwnedByTypes": node}},
    }
    current = {
        "azure.mgmt.computelimit.models": {"class_nodes": {"SharedModel": node}},
        "azure.mgmt.computelimit.types": {"class_nodes": {"SharedModel": node, "OwnedByTypes": node}},
    }

    stable_out, current_out = drop_shadow_types_modules(stable, current)

    assert set(stable_out) == set(stable)
    assert set(current_out) == set(current)


def test_shadow_types_module_removal_not_reported_as_deleted_model():
    # The emitter only generates a `TypedDict` for a model reachable as request input. When a
    # model becomes output-only its `TypedDict` disappears from `types` while the real class
    # stays in `models`. That is not an API removal and must not be reported.
    stable = {
        "azure.mgmt.computelimit.models": {
            "class_nodes": {
                "InputModel": {"type": None, "methods": {}, "properties": {}},
                "OutputOnlyResult": {"type": None, "methods": {}, "properties": {}},
            }
        },
        "azure.mgmt.computelimit.types": {
            "class_nodes": {
                "InputModel": {"type": None, "methods": {}, "properties": {}},
                "OutputOnlyResult": {"type": None, "methods": {}, "properties": {}},
            }
        },
    }

    current = {
        "azure.mgmt.computelimit.models": {
            "class_nodes": {
                "InputModel": {"type": None, "methods": {}, "properties": {}},
                "OutputOnlyResult": {"type": None, "methods": {}, "properties": {}},
            }
        },
        "azure.mgmt.computelimit.types": {
            "class_nodes": {
                # `OutputOnlyResult` is no longer request input, so its TypedDict is gone.
                "InputModel": {"type": None, "methods": {}, "properties": {}},
            }
        },
    }

    checker = compare_report_dicts(stable, current, "azure-mgmt-computelimit", changelog=True)

    assert checker.breaking_changes == []
    assert checker.features_added == []


def test_shadow_types_module_added_model_reported_once():
    # A newly added model shows up in both `models` and `types`; only the `models` entry should
    # be reported.
    stable = {
        "azure.mgmt.computelimit.models": {
            "class_nodes": {"ExistingModel": {"type": None, "methods": {}, "properties": {}}}
        },
        "azure.mgmt.computelimit.types": {
            "class_nodes": {"ExistingModel": {"type": None, "methods": {}, "properties": {}}}
        },
    }
    current = {
        "azure.mgmt.computelimit.models": {
            "class_nodes": {
                "ExistingModel": {"type": None, "methods": {}, "properties": {}},
                "TrustedHostSubscription": {"type": None, "methods": {}, "properties": {}},
            }
        },
        "azure.mgmt.computelimit.types": {
            "class_nodes": {
                "ExistingModel": {"type": None, "methods": {}, "properties": {}},
                "TrustedHostSubscription": {"type": None, "methods": {}, "properties": {}},
            }
        },
    }

    checker = compare_report_dicts(stable, current, "azure-mgmt-computelimit", changelog=True)

    added_models = [fa for fa in checker.features_added if fa[0] == ChangelogTracker.ADDED_CLASS_MSG]
    assert len(added_models) == 1
    _, _, module_name, class_name = added_models[0]
    assert module_name == "azure.mgmt.computelimit.models"
    assert class_name == "TrustedHostSubscription"
    assert not any(fa[2] == "azure.mgmt.computelimit.types" for fa in checker.features_added)


def test_new_class_property_added_init():
    # Testing if a property is added both in the init and at the class level that we only get 1 report for it
    current = {
        "azure.ai.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "type": None,
                    "methods": {
                        "__init__": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                },
                                "new_class_att": {
                                    "default": None,
                                    "param_type": "keyword_only"
                                },
                                "kwargs": {
                                    "default": None,
                                    "param_type": "var_keyword"
                                }
                            },
                            "is_async": False
                        },
                    },
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                        "new_class_att": "str"
                    }
                },
            }
        }
    }

    stable = {
        "azure.ai.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "type": None,
                    "methods": {
                        "__init__": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                },
                                "new_class_att": {
                                    "default": None,
                                    "param_type": "keyword_only"
                                },
                                "kwargs": {
                                    "default": None,
                                    "param_type": "var_keyword"
                                }
                            },
                            "is_async": False
                        },
                    },
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                    }
                },
            }
        }
    }

    bc = ChangelogTracker(stable, current, "azure-ai-contentsafety")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_PROPERTY_MSG
    assert args == ['azure.ai.contentsafety', 'AnalyzeTextResult', 'new_class_att']


def test_added_operation_group_class_not_labeled_as_model():
    # A newly added operation group class must be reported as "Added operation group `X`",
    # not "Added model `X`". It appears in both the sync `...operations` module and the async
    # `...aio.operations` module, but the async cleanup should collapse it into a single entry.
    def _op_group_module():
        return {
            "class_nodes": {
                "ExistingOperations": {
                    "type": None,
                    "methods": {},
                    "properties": {}
                },
                "PrivateLinkResourcesOperations": {
                    "type": None,
                    "methods": {},
                    "properties": {}
                }
            }
        }

    def _stable_op_group_module():
        return {
            "class_nodes": {
                "ExistingOperations": {
                    "type": None,
                    "methods": {},
                    "properties": {}
                }
            }
        }

    current = {
        "azure.mgmt.attestation.operations": _op_group_module(),
        "azure.mgmt.attestation.aio.operations": _op_group_module(),
    }
    stable = {
        "azure.mgmt.attestation.operations": _stable_op_group_module(),
        "azure.mgmt.attestation.aio.operations": _stable_op_group_module(),
    }

    bc = ChangelogTracker(stable, current, "azure-mgmt-attestation")
    bc.run_checks()

    op_group_entries = [fa for fa in bc.features_added if fa[0] == ChangelogTracker.ADDED_OPERATION_GROUP_CLASS_MSG]
    added_model_entries = [fa for fa in bc.features_added if fa[0] == ChangelogTracker.ADDED_CLASS_MSG]

    # Exactly one operation group entry (sync/async duplicate collapsed) and no "Added model".
    assert len(op_group_entries) == 1
    assert not added_model_entries
    _, _, _, class_name = op_group_entries[0]
    assert class_name == "PrivateLinkResourcesOperations"


def test_new_class_property_added_init_only():
    # Testing if we get a report on a new class property added only in the init
    current = {
        "azure.ai.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "methods": {
                        "__init__": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                },
                                "new_class_att": {
                                    "default": None,
                                    "param_type": "keyword_only"
                                },
                                "kwargs": {
                                    "default": None,
                                    "param_type": "var_keyword"
                                }
                            },
                            "is_async": False
                        },
                    },
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                    }
                },
            }
        }
    }

    stable = {
        "azure.ai.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "methods": {
                        "__init__": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                },
                                "kwargs": {
                                    "default": None,
                                    "param_type": "var_keyword"
                                }
                            },
                            "is_async": False
                        },
                    },
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                    }
                },
            }
        }
    }

    bc = ChangelogTracker(stable, current, "azure-ai-contentsafety")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_METHOD_PARAMETER_MSG
    assert args == ['azure.ai.contentsafety', 'AnalyzeTextResult', 'new_class_att', '__init__']


def test_new_class_method_parameter_added():
    # Testing if we get a report on a new class method parameter added
    current = {
        "azure.ai.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "methods": {
                        "__init__": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                },
                                "kwargs": {
                                    "default": None,
                                    "param_type": "var_keyword"
                                }
                            },
                            "is_async": False
                        },
                        "foo": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                },
                                "bar": {
                                    "default": None,
                                    "param_type": "var_keyword"
                                }
                            }
                        }
                    },
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                    }
                },
            }
        }
    }

    stable = {
        "azure.ai.contentsafety": {
            "class_nodes": {
                "AnalyzeTextResult": {
                    "methods": {
                        "__init__": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                },
                                "kwargs": {
                                    "default": None,
                                    "param_type": "var_keyword"
                                }
                            },
                            "is_async": False
                        },
                        "foo": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                },
                            },
                            "is_async": False
                        }
                    },
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                    }
                },
            }
        }
    }

    bc = ChangelogTracker(stable, current, "azure-ai-contentsafety")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_METHOD_PARAMETER_MSG
    assert args == ['azure.ai.contentsafety', 'AnalyzeTextResult', 'bar', 'foo']


@pytest.mark.skip(reason="We need to regenerate the code reports for these tests and update the expected results")
def test_pass_custom_reports_changelog(capsys):
    source_report = "test_stable.json"
    target_report = "test_current.json"

    try:
        main(None, None, None, None, "tests", True, False, False, source_report, target_report)
        out, _ = capsys.readouterr()
        assert "### Breaking Changes" in out
    except SystemExit as e:
        pytest.fail("test_compare_reports failed to report changelog when passing custom reports")


def test_added_operation_group():
    stable = {
        "azure.contoso": {
            "class_nodes": {
                "ContosoClient": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "bar": {
                            "attr_type": "str"
                        }
                    }
                }
            }
        }
    }

    current = {
        "azure.contoso": {
            "class_nodes": {
                "ContosoClient": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "bar": {
                            "attr_type": "str"
                        },
                        "foo": {
                            "attr_type": "DeviceGroupsOperations"
                        },
                        "zip": {
                            "attr_type": "bool"
                        }
                    }
                }
            }
        }
    }

    bc = ChangelogTracker(stable, current, "azure-contoso")
    bc.run_checks()

    assert len(bc.features_added) == 2
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_OPERATION_GROUP_MSG
    assert args == ['azure.contoso', 'ContosoClient', 'foo']
    msg, _, *args = bc.features_added[1]
    assert msg == ChangelogTracker.ADDED_CLASS_PROPERTY_MSG


def test_ignore_changes():
    stable = {
        "azure.contoso": {
            "class_nodes": {
                "ContosoClient": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "bar": {
                            "attr_type": "str"
                        }
                    }
                }
            }
        }
    }

    current = {
        "azure.contoso": {
            "class_nodes": {
                "ContosoClient": {
                    "type": None,
                    "methods": {},
                    "properties": {
                        "bar": {
                            "attr_type": "str"
                        },
                        "foo": {
                            "attr_type": "DeviceGroupsOperations"
                        },
                        "zip": {
                            "attr_type": "bool"
                        }
                    }
                }
            }
        }
    }

    IGNORE = {
        "azure-contoso": [("AddedOperationGroup", "*", "ContosoClient", "foo")]
    }
    bc = ChangelogTracker(stable, current, "azure-contoso", ignore=IGNORE)
    bc.run_checks()
    bc.report_changes()
    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_PROPERTY_MSG


def test_async_features_added_cleanup():
    features_added = [
        ("Message", "AddedClient", "azure.contoso.aio", "FooClient", "foo"),
        ("Message", "AddedClient", "azure.contoso", "FooClient", "foo"),
        ("Message", "AddedClassMethod", "azure.contoso", "FooClient", "from_connection_string"),
    ]

    # create dummy BreakingChangesTracker instance
    ct = ChangelogTracker({}, {}, "azure-contoso")
    ct.features_added = features_added

    ct.run_async_cleanup(ct.features_added)

    assert len(ct.features_added) == 2
    assert ct.features_added[0] == ("Message", "AddedClient", "azure.contoso", "FooClient", "foo")
    assert ct.features_added[1] == ("Message", "AddedClassMethod", "azure.contoso", "FooClient", "from_connection_string")


def test_new_enum_added():
    current = {
        "azure.contoso.widgetmanager": {
            "class_nodes": {
                "WidgetEnum": {
                    "type": "Enum",
                    "methods": {},
                    "properties": {
                        "a": "a",
                        "b": "b",
                    }
                },
                "ManagerEnum": {
                    "type": "Enum",
                    "methods": {},
                    "properties": {
                        "foo": "foo",
                        "bar": "bar",
                    }
                },
            }
        }
    }

    stable = {
        "azure.contoso.widgetmanager": {
            "class_nodes": {
                "ManagerEnum": {
                    "type": "Enum",
                    "methods": {},
                    "properties": {
                        "foo": "foo",
                    }
                },
            }
        }
    }

    bc = ChangelogTracker(stable, current, "azure-contoso-widgetmanager")
    bc.run_checks()

    assert len(bc.features_added) == 2
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_ENUM_MEMBER_MSG
    assert args == ['azure.contoso.widgetmanager', 'ManagerEnum', 'bar']
    msg, _, *args = bc.features_added[1]
    assert msg == ChangelogTracker.ADDED_ENUM_MSG
    assert args == ['azure.contoso.widgetmanager', 'WidgetEnum']


def test_added_overload():
    current = {
        "azure.contoso": {
            "class_nodes": {
                "class_name": {
                    "properties": {},
                    "methods": {
                        "one": {
                            "parameters": {
                                "testing": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True,
                            "overloads": [
                                {
                                    "parameters": {
                                        "testing": {
                                            "type": "Test",
                                            "default": None,
                                            "param_type": "positional_or_keyword"
                                        }
                                    },
                                    "is_async": True,
                                    "return_type": "TestResult"
                                },
                                {
                                    "parameters": {
                                        "testing": {
                                            "type": "JSON",
                                            "default": None,
                                            "param_type": "positional_or_keyword"
                                        }
                                    },
                                    "is_async": True,
                                    "return_type": None
                                }
                            ]
                        },
                        "two": {
                            "parameters": {
                                "testing2": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True,
                            "overloads": [
                                {
                                    "parameters": {
                                        "foo": {
                                            "type": "JSON",
                                            "default": None,
                                            "param_type": "positional_or_keyword"
                                        }
                                    },
                                    "is_async": True,
                                    "return_type": None
                                }
                            ]
                        },
                    }
                }
            }
        }
    }

    stable = {
        "azure.contoso": {
            "class_nodes": {
                "class_name": {
                    "properties": {},
                    "methods": {
                        "one": {
                            "parameters": {
                                "testing": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True,
                            "overloads": [
                                {
                                    "parameters": {
                                        "testing": {
                                            "type": "JSON",
                                            "default": None,
                                            "param_type": "positional_or_keyword"
                                        }
                                    },
                                    "is_async": True,
                                    "return_type": None
                                }
                            ]
                        },
                        "two": {
                            "parameters": {
                                "testing2": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True,
                            "overloads": []
                        },
                    }
                }
            }
        }
    }

    bc = ChangelogTracker(stable, current, "azure-contoso", checkers=[AddedMethodOverloadChecker()])
    bc.run_checks()

    assert len(bc.features_added) == 2
    msg, _, *args = bc.features_added[0]
    assert msg == AddedMethodOverloadChecker.message["default"]
    assert args == ['azure.contoso', 'class_name', 'one', 'def one(testing: Test) -> TestResult']
    msg, _, *args = bc.features_added[1]
    assert msg == AddedMethodOverloadChecker.message["default"]
    assert args == ['azure.contoso', 'class_name', 'two', 'def two(foo: JSON)']


def test_compare_reports_with_absolute_paths(capsys):
    """Verify test_compare_reports accepts absolute paths for source/target reports."""
    tests_dir = os.path.dirname(__file__)
    source_report = os.path.abspath(os.path.join(tests_dir, "examples", "code-reports", "content-safety", "stable.json"))
    target_report = os.path.abspath(os.path.join(tests_dir, "examples", "code-reports", "content-safety", "current.json"))
    pkg_dir = tests_dir  # pkg_dir must exist and is still used (e.g., for package_name and cleanup); its value is independent of using absolute report paths

    # Should not raise; changelog=True means no SystemExit(1) even if breaking changes exist
    compare_reports(pkg_dir, changelog=True, source_report=source_report, target_report=target_report)

    captured = capsys.readouterr()
    assert "===== changelog start =====" in captured.out
    assert "===== changelog end =====" in captured.out


def _make_client_class_node(has_credential: bool):
    init_params = {
        "self": {"default": None, "param_type": "positional_or_keyword"},
        "endpoint": {"default": None, "param_type": "positional_or_keyword"},
    }
    if has_credential:
        init_params["credential"] = {"default": None, "param_type": "positional_or_keyword"}
    return {
        "type": None,
        "methods": {
            "__init__": {
                "parameters": init_params,
                "is_async": False,
            }
        },
        "properties": {},
    }


def test_is_client_non_mgmt_sdk():
    # For non-mgmt SDKs, any class ending with "Client" is considered a client
    # regardless of whether __init__ has a "credential" parameter.
    stable = {"azure.contoso": {"class_nodes": {}}}
    current = {
        "azure.contoso": {
            "class_nodes": {
                "ContosoClient": _make_client_class_node(has_credential=False),
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-contoso")
    assert bc.is_client("azure.contoso", "ContosoClient") is True


def test_is_client_mgmt_sdk_with_credential():
    # For mgmt SDKs, the class name must end with "Client" AND __init__ must
    # accept a "credential" parameter.
    stable = {"azure.mgmt.contoso": {"class_nodes": {}}}
    current = {
        "azure.mgmt.contoso": {
            "class_nodes": {
                "ContosoMgmtClient": _make_client_class_node(has_credential=True),
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-mgmt-contoso")
    assert bc.is_client("azure.mgmt.contoso", "ContosoMgmtClient") is True


def test_is_client_mgmt_sdk_without_credential():
    # A class in a mgmt namespace whose __init__ does not accept a "credential"
    # parameter (e.g. ARMPollingClient) should NOT be treated as a client.
    stable = {"azure.mgmt.contoso": {"class_nodes": {}}}
    current = {
        "azure.mgmt.contoso": {
            "class_nodes": {
                "ARMPollingClient": _make_client_class_node(has_credential=False),
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-mgmt-contoso")
    assert bc.is_client("azure.mgmt.contoso", "ARMPollingClient") is False


def test_is_client_non_client_suffix():
    # Classes whose name does not end with "Client" are never clients.
    stable = {"azure.contoso": {"class_nodes": {}}}
    current = {
        "azure.contoso": {
            "class_nodes": {
                "ContosoModel": {"type": None, "methods": {}, "properties": {}},
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-contoso")
    assert bc.is_client("azure.contoso", "ContosoModel") is False


def test_added_client_mgmt_sdk_with_credential_reported_as_client():
    # Adding a mgmt client whose __init__ takes a "credential" parameter
    # should be reported as a new client.
    existing = {"Existing": {"type": None, "methods": {}, "properties": {}}}
    stable = {"azure.mgmt.contoso": {"class_nodes": dict(existing)}}
    current = {
        "azure.mgmt.contoso": {
            "class_nodes": {
                **existing,
                "ContosoMgmtClient": _make_client_class_node(has_credential=True),
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-mgmt-contoso")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLIENT_MSG
    assert args == ["azure.mgmt.contoso", "ContosoMgmtClient"]


def test_added_client_mgmt_sdk_without_credential_reported_as_class():
    # Adding a mgmt class ending with "Client" but lacking the "credential"
    # parameter (e.g. ARMPollingClient) should be reported as a new model/class,
    # NOT as a new client.
    existing = {"Existing": {"type": None, "methods": {}, "properties": {}}}
    stable = {"azure.mgmt.contoso": {"class_nodes": dict(existing)}}
    current = {
        "azure.mgmt.contoso": {
            "class_nodes": {
                **existing,
                "ARMPollingClient": _make_client_class_node(has_credential=False),
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-mgmt-contoso")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_MSG
    assert args == ["azure.mgmt.contoso", "ARMPollingClient"]


def test_added_client_non_mgmt_sdk_reported_as_client():
    # For non-mgmt SDKs, a class ending with "Client" is always reported as
    # a new client, even if no "credential" parameter exists.
    existing = {"Existing": {"type": None, "methods": {}, "properties": {}}}
    stable = {"azure.contoso": {"class_nodes": dict(existing)}}
    current = {
        "azure.contoso": {
            "class_nodes": {
                **existing,
                "ContosoClient": _make_client_class_node(has_credential=False),
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-contoso")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLIENT_MSG
    assert args == ["azure.contoso", "ContosoClient"]


def _make_client_with_init_kwarg(extra_kwargs=None):
    params = {
        "self": {"default": None, "param_type": "positional_or_keyword"},
        "endpoint": {"default": None, "param_type": "positional_or_keyword"},
        "credential": {"default": None, "param_type": "positional_or_keyword"},
    }
    if extra_kwargs:
        params.update(extra_kwargs)
    return {
        "type": None,
        "methods": {
            "__init__": {
                "parameters": params,
                "is_async": False,
            }
        },
        "properties": {},
    }


def test_added_keyword_only_param_to_mgmt_client_init_reported_as_client():
    # Adding a keyword-only parameter to a mgmt client's __init__ should be
    # reported using the client message, not the model/class message.
    stable = {
        "azure.mgmt.contoso": {
            "class_nodes": {
                "ContosoMgmtClient": _make_client_with_init_kwarg(),
            }
        }
    }
    current = {
        "azure.mgmt.contoso": {
            "class_nodes": {
                "ContosoMgmtClient": _make_client_with_init_kwarg(
                    {"cloud_setting": {"default": None, "param_type": "keyword_only"}}
                ),
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-mgmt-contoso")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLIENT_METHOD_PARAMETER_MSG
    assert args == ["azure.mgmt.contoso", "ContosoMgmtClient", "cloud_setting", "__init__"]


def test_added_keyword_only_param_to_model_method_still_reported_as_class():
    # Adding a keyword-only parameter to a non-client class method should
    # still be reported using the model/class message.
    model_node = {
        "type": None,
        "methods": {
            "do_something": {
                "parameters": {
                    "self": {"default": None, "param_type": "positional_or_keyword"},
                },
                "is_async": False,
            }
        },
        "properties": {},
    }
    model_node_updated = {
        "type": None,
        "methods": {
            "do_something": {
                "parameters": {
                    "self": {"default": None, "param_type": "positional_or_keyword"},
                    "extra": {"default": None, "param_type": "keyword_only"},
                },
                "is_async": False,
            }
        },
        "properties": {},
    }
    stable = {"azure.contoso": {"class_nodes": {"ContosoModel": model_node}}}
    current = {"azure.contoso": {"class_nodes": {"ContosoModel": model_node_updated}}}

    bc = ChangelogTracker(stable, current, "azure-contoso")
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_METHOD_PARAMETER_MSG
    assert args == ["azure.contoso", "ContosoModel", "extra", "do_something"]

def test_added_update_method_for_operation_group():
    stable = {
        "azure.mgmt.contoso.operations": {
            "class_nodes": {
                "ContosoOperations": {
                    "type": None,
                    "methods": {
                        "list": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": False
                        }
                    },
                    "properties": {}
                }
            }
        }
    }
    current = {
        "azure.mgmt.contoso.operations": {
            "class_nodes": {
                "ContosoOperations": {
                    "type": None,
                    "methods": {
                        "list": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": False
                        },
                        "update": {
                            "parameters": {
                                "self": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": False
                        }
                    },
                    "properties": {}
                }
            }
        }
    }
    IGNORE = {
        "azure-mgmt-contoso": [
            ("AddedClassMethod", "*", "*", "update")
        ]
    }
    bc = ChangelogTracker(stable, current, "azure-mgmt-contoso", ignore=IGNORE)
    bc.run_checks()
    bc.report_changes()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_OPERATION_GROUP_METHOD_MSG
    assert args == ["azure.mgmt.contoso.operations", "ContosoOperations", "update"]

def test_added_keyword_only_param_to_operation_group_method():
    stable = {
        "azure.mgmt.contoso.operations": {
            "class_nodes": {
                "ContosoOperations": {
                    "type": None,
                    "methods": {
                        "list": {
                            "parameters": {
                                "self": {"default": None, "param_type": "positional_or_keyword"},
                            },
                            "is_async": False,
                        }
                    },
                    "properties": {},
                }
            }
        }
    }
    current = {
        "azure.mgmt.contoso.operations": {
            "class_nodes": {
                "ContosoOperations": {
                    "type": None,
                    "methods": {
                        "list": {
                            "parameters": {
                                "self": {"default": None, "param_type": "positional_or_keyword"},
                                "extra": {"default": None, "param_type": "keyword_only"},
                            },
                            "is_async": False,
                        }
                    },
                    "properties": {},
                }
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-mgmt-contoso")
    bc.run_checks()
    bc.report_changes()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_OPERATION_GROUP_METHOD_PARAMETER_MSG
    assert args == ["azure.mgmt.contoso.operations", "ContosoOperations", "extra", "list"]

@pytest.mark.parametrize(
    "stable_property,current_property,expected_breaking_changes",
    [
        pytest.param(
            {"attr_type": "Optional[Foo]"}, {"attr_type": "Foo"}, 1, id="optional"
        ),
        pytest.param(
            {"attr_type": "typing.Optional[Foo]"},
            {"attr_type": "Foo"},
            1,
            id="qualified-optional",
        ),
        pytest.param(
            {"attr_type": "Union[Foo, None]"}, {"attr_type": "Foo"}, 1, id="union"
        ),
        pytest.param(
            {"attr_type": "typing.Union[None, Foo]"},
            {"attr_type": "Foo"},
            1,
            id="qualified-union",
        ),
        pytest.param(
            {"attr_type": "Foo | None"}, {"attr_type": "Foo"}, 1, id="pep604-union"
        ),
        pytest.param(
            {"attr_type": "None | Foo"},
            {"attr_type": "Foo"},
            1,
            id="reversed-pep604-union",
        ),
        pytest.param(
            {"attr_type": "Optional[Foo]"},
            {"attr_type": "Union[Foo, None]"},
            0,
            id="optional-to-union",
        ),
        pytest.param(
            {"attr_type": "typing.Optional[Foo]"},
            {"attr_type": "Foo | None"},
            0,
            id="qualified-optional-to-pep604-union",
        ),
        pytest.param(
            {"attr_type": "Union[Foo, None]"},
            {"attr_type": "Optional[Foo]"},
            0,
            id="union-to-optional",
        ),
        pytest.param(
            {"attr_type": "typing.Union[None, Foo]"},
            {"attr_type": "typing.Optional[Foo]"},
            0,
            id="qualified-union-to-qualified-optional",
        ),
        pytest.param(
            {"attr_type": "Foo | None"},
            {"attr_type": "Union[Foo, None]"},
            0,
            id="pep604-union-to-union",
        ),
        pytest.param(
            {"attr_type": "None | Foo"},
            {"attr_type": "typing.Optional[Foo]"},
            0,
            id="reversed-pep604-union-to-qualified-optional",
        ),
        pytest.param(
            {"attr_type": "typing.Optional[Foo]"},
            {"attr_type": "'typing.Optional[Foo]'"},
            0,
            id="quoted-optional",
        ),
        pytest.param(
            {"attr_type": "'typing.Optional[Foo]'"},
            {"attr_type": "Foo"},
            1,
            id="quoted-optional-to-required",
        ),
        pytest.param(
            {"attr_type": "Union[Foo, Union[Bar, None]]"},
            {"attr_type": "Union[Foo, Bar]"},
            1,
            id="nested-union-to-required",
        ),
    ],
)
def test_class_property_is_required(
    stable_property, current_property, expected_breaking_changes
):
    stable = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": {"foo": stable_property},
                }
            }
        }
    }
    current = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": {"foo": current_property},
                }
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-contoso")
    bc.run_checks()
    bc.report_changes()

    assert len(bc.breaking_changes) == expected_breaking_changes
    if expected_breaking_changes:
        msg, _, *args = bc.breaking_changes[0]
        assert msg == ChangelogTracker.REQUIRED_PROPERTY_MSG
        assert args == ["azure.contoso.models", "ContosoModel", "foo"]


def test_class_property_is_required_with_default_report():
    stable_properties = {}
    current_properties = {}
    stable_class = ast.parse(
        "class ContosoModel:\n    foo: Optional[Foo] = rest_field()\n"
    ).body[0]
    current_class = ast.parse(
        "class ContosoModel:\n    foo: Foo = rest_field()\n"
    ).body[0]
    get_property_names(stable_class, stable_properties)
    get_property_names(current_class, current_properties)

    assert stable_properties == {"foo": {"attr_type": "Optional[Foo]"}}
    assert current_properties == {"foo": {"attr_type": "Foo"}}

    stable = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": stable_properties,
                }
            }
        }
    }
    current = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": current_properties,
                }
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-contoso")
    bc.run_checks()
    bc.report_changes()

    assert len(bc.breaking_changes) == 1
    msg, _, *args = bc.breaking_changes[0]
    assert msg == ChangelogTracker.REQUIRED_PROPERTY_MSG
    assert args == ["azure.contoso.models", "ContosoModel", "foo"]


@pytest.mark.parametrize(
    "stable_property,current_property,expected_breaking_changes",
    [
        pytest.param({"attr_type": "str"}, {"attr_type": "int"}, 1, id="simple"),
        pytest.param(
            {"attr_type": "Optional[str]"}, {"attr_type": "Optional[int]"}, 1, id="optional"
        ),
        pytest.param(
            {"attr_type": 'Optional[list["_models.Foo"]]'},
            {"attr_type": 'Optional[list["_models.Bar"]]'},
            1,
            id="nested-model",
        ),
        pytest.param(
            {"attr_type": "dict[str, list[Foo]]"},
            {"attr_type": "dict[str, list[Bar]]"},
            1,
            id="nested-container",
        ),
        pytest.param(
            {"attr_type": "Foo | None"}, {"attr_type": "Bar | None"}, 1, id="pep604-union"
        ),
        pytest.param(
            {"attr_type": "str"}, {"attr_type": "Optional[str]"}, 1, id="added-nullability"
        ),
        pytest.param({"attr_type": "str"}, {"attr_type": "str"}, 0, id="unchanged"),
        pytest.param(
            {"attr_type": "Optional[Foo]"},
            {"attr_type": "typing.Union[None, Foo]"},
            0,
            id="optional-to-union",
        ),
        pytest.param(
            {"attr_type": "typing.Optional[Foo]"},
            {"attr_type": "Foo | None"},
            0,
            id="qualified-optional-to-pep604-union",
        ),
        pytest.param(
            {"attr_type": "Union[Foo, Bar]"}, {"attr_type": "Bar | Foo"}, 0, id="union-order"
        ),
        pytest.param(
            {"attr_type": 'list["Foo"]'}, {"attr_type": "list[Foo]"}, 0, id="forward-reference"
        ),
        pytest.param(
            {"attr_type": 'Literal["old value"]'},
            {"attr_type": 'Literal["new value"]'},
            1,
            id="literal",
        ),
        pytest.param(
            {"attr_type": "list[Optional[Foo]]"},
            {"attr_type": "list[Foo | None]"},
            0,
            id="nested-equivalent-union",
        ),
        pytest.param(
            {"attr_type": "list[Optional[Foo]]"},
            {"attr_type": "list[Foo]"},
            1,
            id="nested-nullability",
        ),
        pytest.param(
            {"attr_type": "typing.List[Foo]"}, {"attr_type": "list[Foo]"}, 0, id="generic-alias"
        ),
        pytest.param({"attr_type": "typing.Dict"}, {"attr_type": "dict"}, 0, id="bare-dict"),
        pytest.param({"attr_type": "List"}, {"attr_type": "list"}, 0, id="bare-list"),
        pytest.param({"attr_type": "typing.Tuple"}, {"attr_type": "tuple"}, 0, id="bare-tuple"),
        pytest.param({"attr_type": "Set"}, {"attr_type": "set"}, 0, id="bare-set"),
        pytest.param(
            {"attr_type": "typing.FrozenSet"}, {"attr_type": "frozenset"}, 0, id="bare-frozenset"
        ),
        pytest.param({"attr_type": "Type"}, {"attr_type": "type"}, 0, id="bare-type"),
        pytest.param(
            {"attr_type": "typing.Optional[Foo]"},
            {"attr_type": "'typing.Optional[Foo]'"},
            0,
            id="quoted-optional",
        ),
        pytest.param("Optional", "Optional[str]", 0, id="incomplete-type"),
        pytest.param({"attr_type": "foo"}, {"attr_type": "str"}, 0, id="initializer-name"),
        pytest.param(None, "str", 0, id="missing-stable-type"),
        pytest.param("str", None, 0, id="missing-current-type"),
        pytest.param("str", "int", 1, id="default-report"),
    ],
)
def test_class_property_type_changed(
    stable_property, current_property, expected_breaking_changes
):
    stable = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": {"foo": stable_property},
                }
            }
        }
    }
    current = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": {"foo": current_property},
                }
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-contoso")
    bc.run_checks()
    bc.report_changes()

    assert len(bc.breaking_changes) == expected_breaking_changes
    if expected_breaking_changes:
        msg, _, *args = bc.breaking_changes[0]
        assert msg == ChangelogTracker.CHANGED_PROPERTY_TYPE_MSG
        stable_type = stable_property["attr_type"] if isinstance(stable_property, dict) else stable_property
        current_type = current_property["attr_type"] if isinstance(current_property, dict) else current_property
        assert args == ["azure.contoso.models", "ContosoModel", "foo", stable_type, current_type]


@pytest.mark.parametrize(
    "stable_type,current_type",
    [
        pytest.param("str", "int", id="simple"),
        pytest.param("Optional[str]", "Optional[int]", id="optional"),
        pytest.param(
            "Optional[list['_models.Foo']]",
            "Optional[list['_models.Bar']]",
            id="nested-model",
        ),
    ],
)
def test_class_property_type_changed_with_default_report(stable_type, current_type):
    stable_properties = {}
    current_properties = {}
    stable_class = ast.parse(
        f"class ContosoModel:\n    foo: {stable_type} = rest_field()\n"
    ).body[0]
    current_class = ast.parse(
        f"class ContosoModel:\n    foo: {current_type} = rest_field()\n"
    ).body[0]
    get_property_names(stable_class, stable_properties)
    get_property_names(current_class, current_properties)

    assert stable_properties == {"foo": {"attr_type": stable_type}}
    assert current_properties == {"foo": {"attr_type": current_type}}

    stable = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": stable_properties,
                }
            }
        }
    }
    current = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": current_properties,
                }
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-contoso")
    bc.run_checks()
    changelog = bc.report_changes()

    assert len(bc.breaking_changes) == 1
    msg, _, *args = bc.breaking_changes[0]
    assert msg == ChangelogTracker.CHANGED_PROPERTY_TYPE_MSG
    assert args == ["azure.contoso.models", "ContosoModel", "foo", stable_type, current_type]
    assert msg.format(*args[1:]) in changelog


def test_class_property_type_unchanged_with_metadata_change():
    stable = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": {"foo": {"attr_type": "Optional[str]", "description": "old"}},
                }
            }
        }
    }
    current = {
        "azure.contoso.models": {
            "class_nodes": {
                "ContosoModel": {
                    "type": None,
                    "methods": {},
                    "properties": {"foo": {"attr_type": "Optional[str]", "description": "new"}},
                }
            }
        }
    }
    bc = ChangelogTracker(stable, current, "azure-contoso")
    bc.run_checks()
    bc.report_changes()

    assert len(bc.breaking_changes) == 0
    assert len(bc.features_added) == 0
