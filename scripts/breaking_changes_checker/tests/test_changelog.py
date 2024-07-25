#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import jsondiff
import pytest
from breaking_changes_checker.changelog_tracker import ChangelogTracker
from breaking_changes_checker.detect_breaking_changes import main


def test_changelog_flag():
    with open(os.path.join(os.path.dirname(__file__), "examples", "code-reports", "content-safety", "stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "examples", "code-reports", "content-safety", "current.json"), "r") as fd:
        current = json.load(fd)
    diff = jsondiff.diff(stable, current)

    bc = ChangelogTracker(stable, current, diff, "azure-ai-contentsafety", changelog=True)
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
                    "methods": {},
                    "properties": {
                        "blocklists_match": "Optional",
                        "categories_analysis": "List[_models.TextCategoriesAnalysis]",
                    }
                },
            }
        }
    }

    diff = jsondiff.diff(stable, current)
    bc = ChangelogTracker(stable, current, diff, "azure-ai-contentsafety", changelog=True)
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_PROPERTY_MSG
    assert args == ['azure.ai.contentsafety', 'AnalyzeTextResult', 'new_class_att']


def test_new_class_property_added_init():
    # Testing if a property is added both in the init and at the class level that we only get 1 report for it
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

    diff = jsondiff.diff(stable, current)
    bc = ChangelogTracker(stable, current, diff, "azure-ai-contentsafety", changelog=True)
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_PROPERTY_MSG
    assert args == ['azure.ai.contentsafety', 'AnalyzeTextResult', 'new_class_att']


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

    diff = jsondiff.diff(stable, current)
    bc = ChangelogTracker(stable, current, diff, "azure-ai-contentsafety", changelog=True)
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

    diff = jsondiff.diff(stable, current)
    bc = ChangelogTracker(stable, current, diff, "azure-ai-contentsafety", changelog=True)
    bc.run_checks()

    assert len(bc.features_added) == 1
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_CLASS_METHOD_PARAMETER_MSG
    assert args == ['azure.ai.contentsafety', 'AnalyzeTextResult', 'bar', 'foo']


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

    diff = jsondiff.diff(stable, current)
    bc = ChangelogTracker(stable, current, diff, "azure-contoso", changelog=True)
    bc.run_checks()

    assert len(bc.features_added) == 2
    msg, _, *args = bc.features_added[0]
    assert msg == ChangelogTracker.ADDED_OPERATION_GROUP_MSG
    assert args == ['azure.contoso', 'ContosoClient', 'foo']
    msg, _, *args = bc.features_added[1]
    assert msg == ChangelogTracker.ADDED_CLASS_PROPERTY_MSG
