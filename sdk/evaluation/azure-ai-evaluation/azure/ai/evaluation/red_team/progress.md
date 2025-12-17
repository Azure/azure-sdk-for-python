# PyRIT FoundryScenario Integration - Progress Tracking

**Last Updated:** 2025-12-17  
**Current Status:** ✅ Planning Complete, Implementation Pending

---

## Approach

We are integrating PyRIT's **FoundryScenario** system into azure-sdk-for-python's red team module to:

1. **Minimize breaking changes** from PyRIT updates
2. **Rapid attack strategy addition** via PyRIT's tag-based system
3. **Reduce maintenance burden** by delegating attack execution to PyRIT

### High-Level Strategy

- **One FoundryScenario per risk category** instead of manual orchestrator creation
- **Strategy mapping layer** to translate `AttackStrategy` → `FoundryStrategy`
- **Preserve public API** - no changes to how users call `RedTeam.scan()`
- **RAI service scoring** via custom scorer integrated with PyRIT framework
- **SQLite memory** for production-grade persistence

---

## Completed Steps

### ✅ Phase 0: Research & Planning

1. **Conducted comprehensive FoundryScenario inventory** (`foundry_scenario_inventory.md`)
   - Documented architecture layers (Scenario → AtomicAttack → AttackStrategy → Executor → Scoring)
   - Mapped all FoundryStrategy enum members to converters/attacks
   - Analyzed composition rules and validation logic
   - Identified default configurations (adversarial target, scoring)

2. **Created detailed technical specification** (`spec.md` v2.0)
   - Designed strategy mapping layer with rationale
   - Documented RAI service scorer integration
   - Planned context preservation via memory labels
   - Outlined 4-phase migration with feature flags
   - Analyzed 3 options for XPIA/IndirectJailbreak support

3. **Identified key design decisions**:
   - ✅ Use SQLite over DuckDB (production-ready, transactional)
   - ✅ Use memory labels over custom data structures (native PyRIT)
   - ✅ Use RAI service simulation endpoint for adversarial chat
   - ✅ Keep custom XPIA logic short-term, file PyRIT feature request long-term

---

## Current Status: Specification Refinement

### 🔄 In Progress

**Updating spec.md and progress.md with corrections:**

1. ✅ **Adversarial Chat Target**:
   - Changed from OpenAI GPT-4o to RAI service simulation endpoint
   - Using `ProxyChatCompletionsModel` pattern from codebase

2. ✅ **SQLite Rationale**:
   - Added comprehensive "Why SQLite?" section
   - Documented production-readiness, ACID guarantees, PyRIT best practices
   - Clarified that `CentralMemory.get_memory_instance()` uses SQLite

3. ✅ **Memory Labels Alternatives**:
   - Explored 3 options: Memory Labels, Custom Extension, Separate Registry
   - Provided tradeoff analysis with pros/cons
   - Recommended memory labels with structured dicts

4. ✅ **Syntax Cleanup**:
   - Fixed all extra spaces after periods (e.g., `self.logger` instead of `self. logger`)
   - Comprehensive document review for code block accuracy

---

## Pending Steps

### ⬜ Phase 1: Implementation (Week 1-2)

**Core Files to Create:**

1. `_utils/strategy_mapping.py` (NEW)
   - `ATTACK_STRATEGY_TO_FOUNDRY_STRATEGY` mapping table
   - `convert_attack_strategy_to_foundry()` function
   - Handle IndirectJailbreak exclusion with clear error message

2. `_scenario_manager.py` (NEW)
   - `ScenarioManager` class with SQLite initialization
   - `create_scenario_for_risk_category()` method
   - RAI service scorer integration via `_create_rai_scoring_config()`
   - Adversarial chat target via RAI simulation endpoint

3. `_result_converter.py` (NEW)
   - `ResultConverter.convert_scenario_result()` method
   - Extract data from PyRIT `ScenarioResult` → `red_team_info` format
   - Query SQLite memory for conversation data

4. **Modify Existing:**
   - `_red_team.py`:
     - Add feature flag: `USE_FOUNDRY_SCENARIOS`
     - Change PyRIT init to SQLite: `initialize_pyrit(memory_db_type=SQLITE, memory_db_path=db_path)`
     - Dual-path logic in `scan()`: old orchestrators vs. FoundryScenario
   - `_utils/_rai_service_scorer.py`:
     - Update to call `evaluate_with_rai_service_sync` function
     - Return true/false scores based on RAI service response

**Feature Flag Pattern:**
```python
# In _red_team.py
USE_FOUNDRY_SCENARIOS = os.environ.get("AZURE_AI_REDTEAM_USE_FOUNDRY", "false").lower() == "true"

async def scan(self, target, ...):
    if USE_FOUNDRY_SCENARIOS:
        return await self._scan_with_foundry(target, ...)
    else:
        return await self._scan_with_orchestrators(target, ...)
```

### ⬜ Phase 2: Testing (Week 3)

1. **Unit Tests:**
   - `test_strategy_mapping.py` - verify all mappings, handle unsupported strategies
   - `test_scenario_manager.py` - scenario creation, SQLite init, RAI scorer setup
   - `test_result_converter.py` - ScenarioResult → red_team_info conversion

2. **Integration Tests:**
   - `test_foundry_integration.py` - full scan with FoundryScenario
   - Compare old vs. new path outputs (validate equivalence)
   - Test all risk categories + attack strategies

3. **Performance Tests:**
   - Measure execution time differences
   - Validate no regression in attack success rates

### ⬜ Phase 3: Rollout (Week 4)

1. Default to Foundry path (flip feature flag default to `"true"`)
2. Add deprecation warnings to old orchestrator code
3. Update documentation and samples
4. Monitor telemetry for issues

### ⬜ Phase 4: Cleanup (Week 5)

1. Remove old orchestrator code paths
2. Remove feature flag entirely
3. Final testing and validation
4. Update CHANGELOG

---

## Current Blockers/Challenges

### 🚧 Open Issues

1. **XPIA/IndirectJailbreak Support:**
   - **Current State:** Not supported in PyRIT FoundryScenario
   - **Short-term Solution:** Keep custom `_apply_xpia_prompts()` logic outside FoundryScenario
   - **Long-term Solution:** File feature request with PyRIT team (see `feature_requests.md`)
   - **Impact:** Medium - blocks full migration until PyRIT adds native XPIA support

2. **Scenario Result Persistence:**
   - **Question:** Export from SQLite to JSONL for compatibility, or adapt result processing to read from SQLite?
   - **Decision Needed:** Before Phase 1 implementation
   - **Recommendation:** Export to JSONL to maintain compatibility with existing tools

3. **Custom Scoring Integration:**
   - **Challenge:** Ensure RAI service scorer works with PyRIT's scoring pipeline
   - **Status:** Design complete (see spec.md), needs implementation validation

---

## Next Actions (Immediate)

1. ✅ **Complete spec.md updates** - incorporate all feedback
2. ✅ **Update progress.md** - this file
3. ⬜ **Create `feature_requests.md`** - document XPIA feature request for PyRIT team
4. ⬜ **Begin Phase 1 implementation** - start with `strategy_mapping.py`
5. ⬜ **Set up SQLite initialization** - modify `_red_team.py.__init__()`

---

## Design Decisions Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Use SQLite over DuckDB | Production-ready, ACID guarantees, PyRIT best practice | 2025-12-17 |
| Memory labels over custom fields | Native PyRIT feature, persisted, queryable | 2025-12-17 |
| RAI simulation endpoint for adversarial chat | Consistency with other simulator components | 2025-12-17 |
| Strategy mapping layer | Maintain public API stability, absorb PyRIT changes | 2025-12-17 |
| Feature flag for gradual rollout | Reduce risk, allow A/B testing | 2025-12-17 |
| Keep XPIA custom logic short-term | Unblock implementation while PyRIT adds support | 2025-12-17 |

---

## References

- **Technical Spec:** `spec.md` (v2.0)
- **FoundryScenario Inventory:** `foundry_scenario_inventory.md`
- **PyRIT Feature Requests:** `feature_requests.md`
- **PyRIT Documentation:** https://github.com/Azure/PyRIT/tree/main/doc
- **FoundryScenario Source:** https://github.com/Azure/PyRIT/blob/main/pyrit/scenario/scenarios/foundry_scenario.py
