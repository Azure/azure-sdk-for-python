# PyRIT FoundryScenario Integration - Technical Specification v3.0

**Last Updated:** 2025-12-18  
**Status:** Planning Complete  
**Owner:** Azure AI Evaluation Team  
**Target PyRIT Version:** 0.10.0

> **Breaking Changes in PyRIT 0.10.0:**
> - DuckDB support removed (SQLite only)
> - `PromptRequestPiece` renamed to `MessagePiece`
> - `get_prompt_request_pieces()` renamed to `get_message_pieces()`

## Executive Summary

This specification outlines the integration of PyRIT's FoundryScenario framework into Azure AI Evaluation's red teaming module. The integration leverages:

- **Message-based data model** using `MessagePiece` for conversation tracking
- **SQLite memory** (only option in PyRIT 0.10.0+) for persistent storage
- **FoundryStrategy** mapping for attack strategy orchestration
- **Memory labels** for context preservation across scan sessions

## Core Components

### Strategy Mapping Layer

**File:** `_utils/strategy_mapping.py`

Maps Azure AI Evaluation's `AttackStrategy` enum to PyRIT's `FoundryStrategy`:

```python
from pyrit.scenario.scenarios.foundry_scenario import FoundryStrategy

ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY: Dict[AttackStrategy, FoundryStrategy] = {
    AttackStrategy.Direct: FoundryStrategy.Jailbreak,
    AttackStrategy.PAIR: FoundryStrategy.Pair,
    AttackStrategy.ROT13: FoundryStrategy.ROT13,
    AttackStrategy.Base64: FoundryStrategy.Base64,
}
```

### Scenario Manager

**File:** `_scenario_manager.py`

Manages FoundryScenario lifecycle and configuration:

- Initialize PyRIT with SQLite (line ~234 breaking change fix)
- Use RAI service simulation endpoint for adversarial chat
- Create FoundryScenario instances per risk category

**Key Responsibilities:**
- Configure memory database paths
- Set up prompt target endpoints
- Manage scenario execution lifecycle
- Handle objective generation and context injection

### Result Converter

**File:** `_result_converter.py`

Converts PyRIT memory data to Azure AI Evaluation results:

- Use `get_message_pieces()` instead of `get_prompt_request_pieces()`
- Access `MessagePiece` properties (not `PromptRequestPiece`)
- Extract conversation history and metadata
- Generate evaluation-compatible result objects

## PyRIT Memory: SQLite (v0.10.0+)

**PyRIT 0.10.0 removed DuckDB support.** SQLite is now the only supported memory backend.

### Implementation

```python
from pyrit.common import initialize_pyrit, SQLITE

# In ScenarioManager.__init__()
db_path = os.path.join(self.output_dir, "pyrit_memory.db")
initialize_pyrit(memory_db_type=SQLITE, memory_db_path=db_path)
```

### Memory Retrieval

```python
from pyrit.memory import CentralMemory

memory = CentralMemory.get_memory_instance()
message_pieces = memory.get_message_pieces(
    labels={"risk_category": risk_category.value}
)
```

## Context Preservation with Memory Labels

Memory labels attach metadata to each conversation turn, enabling filtering and reconstruction:

```python
# Attach labels when creating scenario
scenario._memory_labels = {
    "risk_category": risk_category.value,
    "scan_session_id": scan_session_id,
    "objective": objective,
    "context": context_data,
    "risk_subtype": risk_subtype,
}

# Retrieve during result processing
memory = CentralMemory.get_memory_instance()
message_pieces = memory.get_message_pieces(labels={"risk_category": "violence"})

for piece in message_pieces:
    context = piece.labels.get("context", {})
    risk_subtype = piece.labels.get("risk_subtype", "")
```

## Migration Strategy

### Phase 1: Core Infrastructure (Weeks 1-2)

**⚠️ Breaking Change Alert:** Current `_red_team.py` (line 222) uses:
```python
initialize_pyrit(memory_db_type=DUCK_DB)  # ❌ Removed in PyRIT 0.10.0
```
Must update to:
```python
initialize_pyrit(memory_db_type=SQLITE, memory_db_path=db_path)  # ✅ Only option
```

**Tasks:**
1. Create `_utils/strategy_mapping.py` with FoundryStrategy mappings
2. Update PyRIT initialization in `_red_team.py` to use SQLite
3. Implement `_scenario_manager.py` for FoundryScenario orchestration
4. Add memory label configuration for context preservation

**Deliverables:**
- Working FoundryScenario execution for single risk category
- SQLite memory database with proper labeling
- Unit tests for strategy mapping

### Phase 2: Result Processing (Week 3)

**Tasks:**
1. Implement `_result_converter.py` using `get_message_pieces()`
2. Update `_result_processor.py` to use MessagePiece data model
3. Integrate with existing evaluation pipeline
4. Add result formatting and export logic

**Deliverables:**
- Complete result conversion pipeline
- Integration tests with mock PyRIT scenarios
- Documentation for result schema

### Phase 3: End-to-End Integration (Week 4)

**Tasks:**
1. Connect all components in `_red_team.py`
2. Add error handling and retry logic
3. Implement progress tracking and logging
4. Performance optimization and validation

**Deliverables:**
- Full red team scan execution
- Integration tests covering all attack strategies
- Performance benchmarks

### Phase 4: Testing & Documentation (Week 5)

**Tasks:**
1. Comprehensive unit and integration tests
2. Update API documentation
3. Create migration guide for existing users
4. Add code examples and usage samples

**Deliverables:**
- >90% test coverage
- Published documentation
- Sample notebooks

## Architecture Diagrams

### Component Interaction Flow

```
User API Call
    ↓
RedTeam.scan()
    ↓
ScenarioManager
    ├── Initialize PyRIT (SQLite)
    ├── Create FoundryScenario instances
    └── Execute attack strategies
         ↓
PyRIT Memory (SQLite)
    └── Store MessagePieces with labels
         ↓
ResultConverter
    ├── Query message_pieces by labels
    ├── Extract conversation history
    └── Build RedTeamResult objects
         ↓
RedTeamResult
    └── Return to user
```

### Data Flow

```
Attack Objective
    ↓
FoundryScenario.execute()
    ↓
Adversarial Prompt → Target System → Response
    ↓
MessagePiece (with labels)
    ↓
SQLite Database
    ↓
get_message_pieces(labels=...)
    ↓
RedTeamResult
```

## API Design

### Public Interface (No Changes)

The external API remains unchanged to ensure backward compatibility:

```python
from azure.ai.evaluation.red_team import RedTeam

red_team = RedTeam(...)
result = red_team.scan(
    risk_categories=[RiskCategory.VIOLENCE],
    attack_strategies=[AttackStrategy.Direct, AttackStrategy.PAIR]
)
```

### Internal Changes

All changes are internal implementation details:
- Strategy mapping happens transparently
- Memory storage is abstracted
- Result conversion is automatic

## Testing Strategy

### Unit Tests
- Strategy mapping correctness
- Memory label configuration
- Result conversion logic
- Error handling

### Integration Tests
- End-to-end scenario execution
- Memory persistence and retrieval
- Multi-strategy orchestration
- Context preservation

### Performance Tests
- Scenario execution latency
- Memory query performance
- Result processing throughput
- Resource utilization

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| PyRIT API instability | High | Pin to stable version 0.10.0+ |
| SQLite performance issues | Medium | Optimize query patterns, add indexes |
| Memory label collisions | Low | Use namespaced label keys |
| Breaking changes in future PyRIT versions | Medium | Maintain abstraction layer |

## Success Criteria

1. ✅ All attack strategies execute via FoundryScenario
2. ✅ Context preservation works across scan sessions
3. ✅ Results match existing format (backward compatible)
4. ✅ Performance meets SLA (<5% degradation)
5. ✅ Test coverage >90%
6. ✅ Zero breaking changes to public API

## Appendix

### PyRIT 0.10.0 Breaking Changes Reference

| Old API | New API | Impact |
|---------|---------|--------|
| `DUCK_DB` | `SQLITE` | High - required change |
| `PromptRequestPiece` | `MessagePiece` | High - data model change |
| `get_prompt_request_pieces()` | `get_message_pieces()` | High - method rename |
| `memory_db_type=DUCK_DB` | `memory_db_type=SQLITE, memory_db_path=...` | High - signature change |

### Variable Naming Conventions

Use consistent terminology in code:
- `message_pieces` (not `prompt_request_pieces`)
- `piece` (not `prompt`)
- `get_message_pieces()` (not `get_prompt_request_pieces()`)

### Dependencies

```python
# requirements.txt
pyrit>=0.10.0
```

---

**Document Version History:**
- v3.0 (2025-12-18): Updated for PyRIT 0.10.0 breaking changes
- v2.0 (2025-11-15): Added context preservation strategy
- v1.0 (2025-10-01): Initial specification
