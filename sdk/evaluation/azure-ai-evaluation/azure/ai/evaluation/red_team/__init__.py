# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Use lazy loading to avoid printing messages during import unless the classes are actually used.
_lazy_imports = {}

def _create_lazy_import(class_name, module_path, dependency_name):
    """Create a lazy import function for optional dependencies.
    
    Args:
        class_name: Name of the class to import
        module_path: Module path to import from
        dependency_name: Name of the dependency package for error message
    
    Returns:
        A function that performs the lazy import when called
    """
    def lazy_import():
        try:
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except ImportError:
            raise ImportError(
                f"Could not import {class_name}. Please install the dependency with `pip install {dependency_name}`."
            )
    return lazy_import

_lazy_imports["RedTeam"] = _create_lazy_import("RedTeam", "azure.ai.evaluation.red_team._red_team", "azure-ai-evaluation[redteam]")
_lazy_imports["AttackStrategy"] = _create_lazy_import("AttackStrategy", "azure.ai.evaluation.red_team._attack_strategy", "azure-ai-evaluation[redteam]")
_lazy_imports["RiskCategory"] = _create_lazy_import("RiskCategory", "azure.ai.evaluation.red_team._attack_objective_generator", "azure-ai-evaluation[redteam]")
_lazy_imports["RedTeamResult"] = _create_lazy_import("RedTeamResult", "azure.ai.evaluation.red_team._red_team_result", "azure-ai-evaluation[redteam]")

__all__ = [
    "RedTeam",
    "AttackStrategy",
    "RiskCategory",
    "RedTeamResult",
]


def __getattr__(name):
    """Handle lazy imports for optional dependencies."""
    if name in _lazy_imports:
        return _lazy_imports[name]()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
