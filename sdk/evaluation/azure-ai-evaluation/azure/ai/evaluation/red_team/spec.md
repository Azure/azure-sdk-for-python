# PyRIT FoundryScenario Integration - Technical Specification v2.0

**Last Updated:** 2025-12-17  
**Status:** Planning Complete  
**Owner:** Azure AI Evaluation Team  
**Target PyRIT Version:** 0.10.0

> **Note:** This specification targets PyRIT 0.10.0, which removed DuckDB support. SQLite is now the only supported memory backend.

## Overview

This specification outlines the technical approach for integrating PyRIT's FoundryScenario into Azure AI Evaluation's red teaming framework.

## PyRIT Memory: SQLite (v0.10.0+)

**PyRIT 0.10.0 removed DuckDB support.** SQLite is now the only supported memory backend.

### Implementation

```python
from pyrit.common import initialize_pyrit, SQLITE

# In RedTeam.__init__() or ScenarioManager.__init__()
db_path = os.path.join(self.output_dir, "pyrit_memory.db")
initialize_pyrit(memory_db_type=SQLITE, memory_db_path=db_path)
```

### Memory Retrieval

When retrieving results from PyRIT memory:

```python
from pyrit.memory import CentralMemory

# CentralMemory uses the SQLite backend configured during initialization
memory = CentralMemory.get_memory_instance()

# Query by labels (stored in SQLite)
message_pieces = memory.get_message_pieces(
    labels={"risk_category": risk_category.value}
)
```

**Note:** `CentralMemory.get_memory_instance()` returns the **singleton instance** that uses the SQLite backend configured during `initialize_pyrit()`.

## Implementation Phases

### ⬜ Phase 1: Implementation (Week 1-2)

**Breaking Change Alert:** Current `_red_team.py` uses `initialize_pyrit(memory_db_type=DUCK_DB)` which was removed in PyRIT 0.10.0. Must update to SQLite before implementing FoundryScenario.

**Core Files to Create:**
- `_foundry_scenario.py`: FoundryScenario implementation
- `_scenario_manager.py`: Scenario lifecycle management

**Files to Modify:**
- `_red_team.py`: Update PyRIT initialization to use SQLite
- `_orchestrator_manager.py`: Integration points for FoundryScenario

### ⬜ Phase 2: Testing & Validation (Week 3)

**Testing Strategy:**
- Unit tests for FoundryScenario components
- Integration tests with existing red team framework
- End-to-end scenario execution tests

### ⬜ Phase 3: Documentation & Release (Week 4)

**Deliverables:**
- API documentation
- Migration guide for existing red team usage
- Sample scenarios and usage examples

## Technical Requirements

### Dependencies
- PyRIT >= 0.10.0 (SQLite backend only)
- Azure AI Evaluation SDK
- Python >= 3.9

### Configuration
- SQLite database path configurable via output directory
- Memory persistence across scan sessions
- Label-based query support for result retrieval

## Success Metrics

- [ ] All existing red team functionality preserved
- [ ] FoundryScenario successfully integrated
- [ ] SQLite memory backend properly configured
- [ ] No performance degradation compared to current implementation
- [ ] Comprehensive test coverage (>90%)

## References

- [PyRIT Documentation](https://github.com/Azure/PyRIT)
- [Azure AI Evaluation SDK](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/evaluation/azure-ai-evaluation)
