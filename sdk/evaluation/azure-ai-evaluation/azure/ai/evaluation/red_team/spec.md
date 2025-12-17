# PyRIT FoundryScenario Integration - Technical Specification v2.0

**Last Updated:** 2025-12-17  
**Status:** Planning Complete  
**Owner:** Azure AI Evaluation Team

---

## Executive Summary

This specification outlines the integration of PyRIT's **FoundryScenario** system into azure-sdk-for-python's red team module. The goal is to:

1. **Minimize breaking changes** from PyRIT updates by delegating attack execution to PyRIT's stable API
2. **Enable rapid attack strategy addition** via PyRIT's tag-based system
3. **Reduce maintenance burden** by leveraging PyRIT's orchestration layer
4. **Preserve public API** - no changes to how users call `RedTeam.scan()`

### High-Level Approach

- **One FoundryScenario per risk category** instead of manual orchestrator creation
- **Strategy mapping layer** to translate `AttackStrategy` → `FoundryStrategy`
- **RAI service scoring** via custom scorer integrated with PyRIT framework
- **SQLite memory** for production-grade persistence

---

## Architecture Overview

### Current Architecture (Pre-FoundryScenario)

```
RedTeam.scan()
  └─> OrchestratorManager
       ├─> Creates custom orchestrators per strategy
       ├─> Manually constructs converters
       ├─> Manually constructs scorers
       └─> Returns JSONL results
```

**Challenges:**
- PyRIT updates require updating orchestrator construction logic
- Adding new attack strategies requires code changes
- Duplicated configuration across orchestrators
- Manual memory management with DuckDB

### Target Architecture (With FoundryScenario)

```
RedTeam.scan()
  └─> ScenarioManager
       ├─> Creates FoundryScenario per risk category
       │    ├─> Automatically loads strategies via tags
       │    ├─> Automatically configures converters
       │    └─> Uses RAI service scorer
       ├─> SQLite memory for persistence
       └─> ResultConverter transforms ScenarioResult → red_team_info
```

**Benefits:**
- PyRIT updates handled by FoundryScenario abstraction
- Adding attack strategies = updating mapping table
- Centralized configuration
- Production-grade SQLite memory

---

## Core Components

### 1. Strategy Mapping Layer

**File:** `_utils/strategy_mapping.py` (NEW)

**Purpose:** Translate azure-sdk-for-python's `AttackStrategy` enum to PyRIT's `FoundryStrategy` enum.

**Implementation:**

```python
from enum import Enum
from typing import Dict, Optional
from pyrit.scenario.attack_strategy import FoundryStrategy
from .._attack_strategy import AttackStrategy

# Mapping table: AttackStrategy → FoundryStrategy
ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY: Dict[AttackStrategy, FoundryStrategy] = {
    # Direct jailbreak attacks
    AttackStrategy.Direct: FoundryStrategy.CRESCENDO,
    
    # Multi-turn attacks
    AttackStrategy.PAIR: FoundryStrategy.PAIR,
    
    # Code injection
    AttackStrategy.CodeInjection: FoundryStrategy.CODE_INJECTION,
    
    # Add more mappings as needed
    # AttackStrategy.XYZ: FoundryStrategy.ABC,
}

def convert_attack_strategy_to_foundry(strategy: AttackStrategy) -> FoundryStrategy:
    """
    Convert azure-sdk-for-python AttackStrategy to PyRIT FoundryStrategy.
    
    Args:
        strategy: The attack strategy to convert
        
    Returns:
        Corresponding FoundryStrategy
        
    Raises:
        ValueError: If strategy is not supported in FoundryScenario
    """
    if strategy not in ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY:
        raise ValueError(
            f"Attack strategy {strategy} is not supported with FoundryScenario. "
            f"Supported strategies: {list(ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY.keys())}"
        )
    
    return ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY[strategy]
```

**Design Rationale:**

1. **Centralized Mapping:** Single source of truth for strategy translation
2. **Clear Error Messages:** Explicit feedback when strategy is unsupported
3. **Easy Extension:** Adding new strategies = one line in mapping table
4. **Type Safety:** Enum-to-enum mapping prevents typos

**Future Work:**
- When PyRIT adds XPIA/IndirectJailbreak support, add to mapping table:
  ```python
  AttackStrategy.XPIA: FoundryStrategy.XPIA,
  AttackStrategy.IndirectJailbreak: FoundryStrategy.INDIRECT_JAILBREAK,
  ```

---

### 2. Scenario Manager

**File:** `_scenario_manager.py` (NEW)

**Purpose:** Create and configure FoundryScenarios for risk categories.

**Key Responsibilities:**
1. Initialize PyRIT with SQLite memory
2. Create FoundryScenario instances per risk category
3. Configure RAI service scoring
4. Configure adversarial chat target

**Implementation Outline:**

```python
from typing import List, Dict, Optional
from pathlib import Path
import os

from pyrit.common import initialize_pyrit, SQLITE
from pyrit.scenario import FoundryScenario
from pyrit.scenario.attack_strategy import FoundryStrategy
from pyrit.prompt_target import PromptChatTarget
from pyrit.memory import CentralMemory

from .._attack_objective_generator import RiskCategory
from ._strategy_mapping import convert_attack_strategy_to_foundry
from ._rai_service_scorer import RAIServiceScorer

class ScenarioManager:
    """Manages FoundryScenario creation and execution."""
    
    def __init__(self, output_dir: Path, rai_client, token_manager, logger):
        self.output_dir = output_dir
        self.rai_client = rai_client
        self.token_manager = token_manager
        self.logger = logger
        
        # Initialize PyRIT with SQLite
        db_path = os.path.join(self.output_dir, "pyrit_memory.db")
        initialize_pyrit(memory_db_type=SQLITE, memory_db_path=db_path)
        self.logger.info(f"Initialized PyRIT with SQLite at {db_path}")
    
    def _get_default_adversarial_target(self):
        """Get default adversarial target using RAI service simulation endpoint."""
        from azure.ai.evaluation.simulator._model_tools._proxy_completion_model import ProxyChatCompletionsModel
        from azure.ai.evaluation._common.onedp._client import ProjectsClient as AIProjectClient
        
        # Use RAI service simulation endpoint for adversarial chat
        # This ensures consistency with other simulator components
        endpoint_url = (
            self.rai_client._config.endpoint + "/redTeams/simulation/chat/completions/submit"
            if isinstance(self.rai_client, AIProjectClient)
            else self.rai_client.simulation_submit_endpoint
        )
        
        return ProxyChatCompletionsModel(
            name="rai_adversarial_model",
            template_key="adversarial_template",
            template_parameters={},
            endpoint_url=endpoint_url,
            token_manager=self.token_manager,
            api_version="2023-07-01-preview",
            max_tokens=1200,
            temperature=1.2,
        )
    
    def _create_rai_scoring_config(self):
        """Create RAI service scorer configuration."""
        return RAIServiceScorer(
            rai_client=self.rai_client,
            token_manager=self.token_manager,
        )
    
    def create_scenario_for_risk_category(
        self,
        risk_category: RiskCategory,
        attack_strategies: List[AttackStrategy],
        target: PromptChatTarget,
        objectives: List[str],
        prompt_to_context: Dict[str, Dict],
        prompt_to_risk_subtype: Dict[str, str],
        scan_session_id: str,
    ) -> FoundryScenario:
        """
        Create a FoundryScenario for a specific risk category.
        
        Args:
            risk_category: The risk category to test
            attack_strategies: List of attack strategies to use
            target: The target system to attack
            objectives: List of attack objectives
            prompt_to_context: Mapping of objectives to context data
            prompt_to_risk_subtype: Mapping of objectives to risk subtypes
            scan_session_id: Unique identifier for this scan session
            
        Returns:
            Configured FoundryScenario instance
        """
        # Convert attack strategies
        foundry_strategies = [
            convert_attack_strategy_to_foundry(s) for s in attack_strategies
        ]
        
        # Create scenario
        scenario = FoundryScenario(
            prompt_target=target,
            strategies=foundry_strategies,
            adversarial_chat=self._get_default_adversarial_target(),
            scorer=self._create_rai_scoring_config(),
        )
        
        # Attach memory labels to preserve context
        memory_labels = {
            "risk_category": risk_category.value,
            "scan_session_id": scan_session_id,
        }
        
        # For each objective, attach specific labels
        for objective in objectives:
            context_data = prompt_to_context.get(objective, {})
            risk_subtype = prompt_to_risk_subtype.get(objective, "")
            
            objective_labels = {
                **memory_labels,
                "objective": objective,
                "context": context_data,
                "risk_subtype": risk_subtype,
            }
            
            # PyRIT will use these labels when storing conversation in SQLite
            scenario.memory_labels = objective_labels
        
        return scenario
```

---

### 3. Result Converter

**File:** `_result_converter.py` (NEW)

**Purpose:** Convert PyRIT `ScenarioResult` to azure-sdk-for-python's `red_team_info` format.

**Implementation Outline:**

```python
from typing import Dict, List, Any
from pyrit.scenario import ScenarioResult
from pyrit.memory import CentralMemory
from .._attack_objective_generator import RiskCategory

class ResultConverter:
    """Converts PyRIT ScenarioResult to red_team_info format."""
    
    @staticmethod
    def convert_scenario_result(
        result: ScenarioResult,
        risk_category: RiskCategory,
    ) -> Dict[str, Any]:
        """
        Convert ScenarioResult to red_team_info dictionary.
        
        Args:
            result: PyRIT ScenarioResult
            risk_category: Risk category for this scenario
            
        Returns:
            Dictionary in red_team_info format
        """
        memory = CentralMemory.get_memory_instance()
        
        # Query SQLite for all prompts in this risk category
        prompts = memory.get_prompt_request_pieces(
            labels={"risk_category": risk_category.value}
        )
        
        red_team_info = []
        
        for prompt in prompts:
            # Extract context from labels
            context = prompt.labels.get("context", {})
            risk_subtype = prompt.labels.get("risk_subtype", "")
            objective = prompt.labels.get("objective", "")
            
            # Build red_team_info entry
            entry = {
                "objective": objective,
                "risk_category": risk_category.value,
                "risk_subtype": risk_subtype,
                "context": context,
                "conversation": [
                    {
                        "role": prompt.role,
                        "content": prompt.content,
                    }
                ],
                "score": prompt.score if hasattr(prompt, "score") else None,
            }
            
            red_team_info.append(entry)
        
        return {"red_team_info": red_team_info}
```

---

## Why SQLite for PyRIT Memory?

### Decision Rationale

PyRIT supports both DuckDB and SQLite as memory backends. We are switching to **SQLite** for the following reasons:

1. **Production Readiness**:
   - SQLite is battle-tested with billions of deployments
   - DuckDB is newer and optimized for analytics, not transactional workloads
   - PyRIT memory operations are transactional (insert conversation, query by labels)

2. **Persistence & Reliability**:
   - SQLite provides ACID guarantees for concurrent access
   - File-based persistence is more predictable than DuckDB's columnar storage
   - Better recovery from crashes or interruptions

3. **PyRIT Best Practices**:
   - PyRIT team recommends SQLite for production scenarios
   - DuckDB is intended for experimentation and analytics
   - Most PyRIT examples use SQLite

4. **Performance Characteristics**:
   - SQLite faster for row-oriented operations (inserting/querying conversations)
   - DuckDB optimized for column-scans (not our primary use case)
   - Memory footprint is smaller with SQLite

5. **Ecosystem Compatibility**:
   - SQLite has better Python ecosystem support (sqlite3 in stdlib)
   - DuckDB requires additional dependencies
   - Easier debugging with standard SQLite tools

### Implementation

```python
from pyrit.common import initialize_pyrit, SQLITE

# In RedTeam.__init__()
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
prompts = memory.get_prompt_request_pieces(
    labels={"risk_category": risk_category.value}
)
```

**Note:** `CentralMemory.get_memory_instance()` returns the **singleton instance** that uses the SQLite backend configured during `initialize_pyrit()`. There is no confusion about database backend—it's SQLite throughout.

---

## Context Preservation: Memory Labels vs. Alternatives

### The Challenge

We need to preserve context information (baseline context, XPIA context, risk_subtype) throughout the attack execution pipeline so it's available during scoring and result processing.

Current approach uses PyRIT's **memory labels** attached to each `PromptRequestPiece`. We explore three alternatives:

### Option 1: Memory Labels (Current Choice)

**Approach:**
```python
# Attach labels when running atomic attack
atomic_attack.memory_labels = {
    "risk_category": risk_category.value,
    "scan_session_id": scan_session_id,
    "objective": objective,
    "context": context_data,  # Dict with "contexts" list
    "risk_subtype": risk_subtype,
}

# Retrieve during result processing
memory = CentralMemory.get_memory_instance()
prompts = memory.get_prompt_request_pieces(labels={"risk_category": "violence"})

for prompt in prompts:
    context = prompt.labels.get("context", {})
    risk_subtype = prompt.labels.get("risk_subtype", "")
```

**Pros:**
- ✅ Native PyRIT feature (stable API)
- ✅ Persisted in SQLite with conversation data
- ✅ Queryable via memory interface
- ✅ No custom data structures needed
- ✅ Works with PyRIT's existing scorers

**Cons:**
- ❌ Labels are key-value pairs (strings/dicts), not strongly typed
- ❌ Nested structures (contexts list) require dict serialization
- ❌ PyRIT doesn't validate label schemas

**Verdict:** ✅ **Best option** - leverages existing PyRIT infrastructure

---

### Option 2: Custom PromptRequestPiece Extension

**Approach:**
```python
from pyrit.models import PromptRequestPiece
from dataclasses import dataclass

@dataclass
class FoundryPromptRequestPiece(PromptRequestPiece):
    """Extended PromptRequestPiece with Foundry-specific fields."""
    baseline_context: Optional[str] = None
    xpia_context: Optional[Dict] = None
    risk_subtype: Optional[str] = None
    attack_technique: Optional[str] = None
    
# Use in orchestrator
request = FoundryPromptRequestPiece(
    role="user",
    content=objective,
    baseline_context=baseline_context,
    xpia_context=xpia_wrapper,
    risk_subtype="hate_speech",
)
```

**Pros:**
- ✅ Strongly typed fields
- ✅ IDE autocomplete and type checking
- ✅ Clear schema definition

**Cons:**
- ❌ **PyRIT scorers expect base `PromptRequestPiece`** - won't recognize custom fields
- ❌ Requires patching PyRIT memory to persist custom fields
- ❌ Not compatible with `CentralMemory.add_request_pieces_to_memory()`
- ❌ Would need custom serialization/deserialization

**Verdict:** ❌ Not viable - breaks PyRIT compatibility

---

### Option 3: Separate Context Tracking Dictionary

**Approach:**
```python
# Maintain separate mapping in RedTeam instance
class ScenarioManager:
    def __init__(self):
        self.context_registry = {}  # prompt_id -> context_data
    
    async def run_scenario_async(self, scenario):
        for objective in objectives:
            prompt_id = str(uuid.uuid4())
            
            # Store context separately
            self.context_registry[prompt_id] = {
                "baseline_context": baseline_context,
                "xpia_context": xpia_wrapper,
                "risk_subtype": risk_subtype,
            }
            
            # Run attack with ID in labels
            await attack.run_async(objective, labels={"prompt_id": prompt_id})
        
        # Later retrieval
        context_data = self.context_registry[prompt_id]
```

**Pros:**
- ✅ Full control over data structure
- ✅ No PyRIT constraints on schema
- ✅ Can use complex Python objects

**Cons:**
- ❌ **Not persisted** - lost if process crashes
- ❌ Requires passing registry through entire pipeline
- ❌ Race conditions in async execution
- ❌ No queryability via PyRIT memory interface
- ❌ Duplicate state management

**Verdict:** ❌ Not viable - loses persistence benefits

---

### Recommendation: Use Memory Labels with Structured Dicts

**Implementation Pattern:**

```python
# In ScenarioManager.create_scenario_for_risk_category()
memory_labels = {
    "risk_category": risk_category.value,
    "scan_session_id": scan_session_id,
}

# For each objective, attach specific labels
for objective in objectives:
    context_data = prompt_to_context.get(objective, {})
    risk_subtype = prompt_to_risk_subtype.get(objective, "")
    
    objective_labels = {
        **memory_labels,
        "objective": objective,
        "context": context_data,  # Structured dict: {"contexts": [...]}
        "risk_subtype": risk_subtype,
    }
    
    # PyRIT stores these in SQLite conversation.labels column (JSON)
    await atomic_attack.run_async(objective, labels=objective_labels)

# Retrieval in ResultConverter
prompts = memory.get_prompt_request_pieces(labels={"risk_category": "violence"})

for prompt in prompts:
    # Extract structured context
    context = prompt.labels.get("context", {})
    contexts_list = context.get("contexts", [])
    
    for ctx in contexts_list:
        content = ctx.get("content", "")
        tool_name = ctx.get("tool_name", "")
        context_type = ctx.get("context_type", "")
```

**Why This Works:**
- PyRIT serializes label dicts to JSON in SQLite
- Nested structures preserved through serialization
- Query by top-level keys (risk_category, scan_session_id)
- Extract nested data during post-processing
- No PyRIT API changes needed

---

## Migration Strategy

### Phase 1: Implement with Feature Flag (Week 1-2)

**Add new code paths without removing old ones:**

```python
# In _red_team.py
USE_FOUNDRY_SCENARIOS = os.environ.get("AZURE_AI_REDTEAM_USE_FOUNDRY", "false").lower() == "true"

async def scan(self, target, ...):
    if USE_FOUNDRY_SCENARIOS:
        return await self._scan_with_foundry(target, ...)
    else:
        return await self._scan_with_orchestrators(target, ...)
```

**New files to create:**
- `_utils/strategy_mapping.py` - AttackStrategy → FoundryStrategy mapping
- `_scenario_manager.py` - FoundryScenario creation and configuration
- `_result_converter.py` - ScenarioResult → red_team_info conversion

**Modify existing files:**
- `_red_team.py` - add feature flag, change PyRIT init to SQLite, dual-path logic

### Phase 2: Testing & Validation (Week 3)

1. Unit tests for new components
2. Integration tests comparing old vs. new path outputs
3. Performance testing (ensure no regression)
4. Documentation updates

### Phase 3: Gradual Rollout (Week 4)

1. Default feature flag to `"true"`
2. Add deprecation warnings to old code path
3. Monitor telemetry for issues
4. Gather feedback

### Phase 4: Cleanup (Week 5)

1. Remove old orchestrator code paths
2. Remove feature flag
3. Final testing and validation
4. Update CHANGELOG

---

## XPIA/IndirectJailbreak Support

### Current State

PyRIT's FoundryScenario does **not currently support** XPIA or IndirectJailbreak attack strategies.

### Short-Term Solution

Keep custom XPIA logic outside FoundryScenario:

```python
async def scan(self, target, ...):
    if USE_FOUNDRY_SCENARIOS:
        # Check if XPIA/IndirectJailbreak requested
        if AttackStrategy.XPIA in attack_strategies or AttackStrategy.IndirectJailbreak in attack_strategies:
            # Use custom orchestrator for XPIA
            return await self._scan_with_custom_xpia(target, ...)
        else:
            # Use FoundryScenario for other strategies
            return await self._scan_with_foundry(target, ...)
    else:
        return await self._scan_with_orchestrators(target, ...)
```

### Long-Term Solution

File feature request with PyRIT team to add XPIA support to FoundryStrategy enum and FoundryScenario. Once added, update strategy mapping:

```python
ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY = {
    ...
    AttackStrategy.XPIA: FoundryStrategy.XPIA,  # When PyRIT adds support
    AttackStrategy.IndirectJailbreak: FoundryStrategy.INDIRECT_JAILBREAK,  # When PyRIT adds support
}
```

---

## Testing Strategy

### Unit Tests

1. **test_strategy_mapping.py**
   - Verify all supported strategies map correctly
   - Test error handling for unsupported strategies
   - Validate mapping table completeness

2. **test_scenario_manager.py**
   - Test FoundryScenario creation
   - Validate SQLite initialization
   - Test RAI scorer configuration
   - Test adversarial target configuration

3. **test_result_converter.py**
   - Test ScenarioResult → red_team_info conversion
   - Validate context extraction from labels
   - Test edge cases (missing labels, empty results)

### Integration Tests

1. **test_foundry_integration.py**
   - Full scan with FoundryScenario
   - Compare old vs. new path outputs
   - Test all risk categories
   - Test all attack strategies

### Performance Tests

1. Measure execution time differences
2. Validate no regression in attack success rates
3. Monitor memory usage

---

## Open Questions

1. **JSONL Export:** Should we export from SQLite to JSONL for compatibility, or adapt result processing to read from SQLite?
   - **Recommendation:** Export to JSONL to maintain compatibility with existing tools

2. **Custom Scorer Integration:** How to best integrate RAI service scorer with PyRIT's scoring pipeline?
   - **Status:** Design complete, needs implementation validation

3. **Backwards Compatibility:** Should we maintain JSONL file format exactly, or can we enhance it?
   - **Recommendation:** Maintain exact format to avoid breaking existing consumers

---

## Success Criteria

1. ✅ All existing `RedTeam.scan()` tests pass with feature flag enabled
2. ✅ No breaking changes to public API
3. ✅ Result format matches existing JSONL structure
4. ✅ SQLite memory properly initialized and queryable
5. ✅ RAI service scorer integrated with PyRIT framework
6. ✅ All attack strategies (except XPIA/IndirectJailbreak) supported
7. ✅ Performance comparable to existing implementation

---

## References

- **PyRIT FoundryScenario Documentation:** https://github.com/Azure/PyRIT/blob/main/doc/code/orchestrators/6_foundry_scenario.md
- **PyRIT Memory Documentation:** https://github.com/Azure/PyRIT/blob/main/doc/code/memory/5_memory.ipynb
- **PyRIT Attack Strategies:** https://github.com/Azure/PyRIT/blob/main/pyrit/scenario/attack_strategy.py
- **FoundryScenario Inventory:** `foundry_scenario_inventory.md`
- **Progress Tracking:** `progress.md`
