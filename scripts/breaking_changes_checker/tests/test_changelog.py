#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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
from breaking_changes_checker.detect_breaking_changes import compare_report_dicts, drop_shadow_types_modules
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

