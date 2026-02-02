# PyRIT FoundryScenario Integration - Progress Tracker

**Last Updated:** 2025-12-18  
**Current Phase:** Phase 1 - Implementation In Progress  
**Next Milestone:** Complete Core Components

## Completed Steps

### ✅ Phase 0: Planning (Completed 2025-12-17)
- [x] Conducted comprehensive FoundryScenario inventory
- [x] Created detailed technical specification (spec.md v3.0)
- [x] Identified breaking changes in PyRIT 0.10.0
- [x] Designed strategy mapping layer
- [x] Planned 4-phase migration strategy

### 🔄 Phase 1: Implementation (In Progress - Started 2025-12-18)

**Completed:**
- [x] Fixed breaking change: `DUCK_DB` → `SQLITE` in `_red_team.py` (line 58)
- [x] Updated initialization call in `_red_team.py` (line 221-225): use `SQLITE` with `memory_db_path`
- [x] Created `_utils/strategy_mapping.py` with FoundryStrategy mapping
- [x] Updated imports to use `SQLITE` instead of `DUCK_DB`
- [x] Added logging statement for SQLite database path

**In Progress:**
- [ ] Create `_scenario_manager.py` for FoundryScenario lifecycle management
- [ ] Create `_result_converter.py` for MessagePiece → red_team_info conversion
- [ ] Add feature flag `USE_FOUNDRY_SCENARIOS` to `_red_team.py`
- [ ] Implement dual-path logic in `scan()` method

**Blocked:**
- IndirectJailbreak (XPIA) strategy - not yet supported in PyRIT FoundryScenario
  - Workaround: Keep custom XPIA logic outside FoundryScenario temporarily

## Current Implementation Status

### Breaking Changes Fixed

| Change | Status | Notes |
|--------|--------|-------|
| `DUCK_DB` → `SQLITE` | ✅ Complete | Line 58 in `_red_team.py` |
| Import path updated | ✅ Complete | `from pyrit.common import SQLITE` |
| Database path configuration | ✅ Complete | Uses `output_dir/pyrit_memory.db` |
| Initialize call updated | ✅ Complete | Line 221-225 with `memory_db_path` parameter |

### Components Status

| Component | Status | File | Notes |
|-----------|--------|------|-------|
| Strategy Mapping | ✅ Complete | `_utils/strategy_mapping.py` | Maps AttackStrategy → FoundryStrategy |
| Scenario Manager | ⬜ Pending | `_scenario_manager.py` | TODO |
| Result Converter | ⬜ Pending | `_result_converter.py` | TODO |
| Feature Flag | ⬜ Pending | `_red_team.py` | TODO |

## Issues Encountered

### 1. PyRIT 0.10.0 API Changes
**Issue:** PromptRequestPiece renamed to MessagePiece  
**Impact:** Medium - affects all memory queries  
**Resolution:** Use `MessagePiece` and `get_message_pieces()` consistently  
**Status:** ✅ Documented in spec.md

### 2. DuckDB Removal
**Issue:** `DUCK_DB` constant no longer exists in PyRIT  
**Impact:** High - blocking import  
**Resolution:** Changed to `SQLITE` with explicit db_path  
**Status:** ✅ Fixed in _red_team.py line 58 and line 221-225

### 3. IndirectJailbreak Strategy
**Issue:** PyRIT FoundryScenario doesn't support XPIA/IndirectJailbreak  
**Impact:** Medium - one strategy unsupported  
**Resolution:** Keep custom XPIA logic outside FoundryScenario (temporary)  
**Status:** 🔄 Workaround implemented, feature request pending

### 4. PAIR Strategy Not in Enum
**Issue:** PAIR strategy mentioned in spec but not in AttackStrategy enum  
**Impact:** Low - mapping adjustment needed  
**Resolution:** Excluded PAIR from strategy mapping (not available in enum)  
**Status:** ✅ Mapping created without PAIR

## Open Questions

1. **Memory Labels for Context Preservation**
   - Question: Can we store nested dicts (contexts list) in memory labels?
   - Answer: Yes - PyRIT serializes labels to JSON in SQLite
   - Status: ✅ Resolved

2. **Baseline Attack Handling**
   - Question: Should baseline use FoundryScenario or stay separate?
   - Answer: Use `include_baseline=True` in FoundryScenario
   - Status: ✅ Resolved

3. **Result Format Compatibility**
   - Question: Does FoundryScenario output match existing JSONL format?
   - Answer: Needs transformation via ResultConverter
   - Status: ⬜ To be verified in testing

## Next Steps (Immediate)

1. **Create Scenario Manager** (priority: high)
   - [ ] Implement `ScenarioManager` class
   - [ ] Add SQLite initialization
   - [ ] Configure RAI service scorer
   - [ ] Set up adversarial chat target

2. **Create Result Converter** (priority: high)
   - [ ] Implement `ResultConverter` class
   - [ ] Extract data from MessagePiece
   - [ ] Build red_team_info format
   - [ ] Handle context/risk_subtype mapping

3. **Add Feature Flag** (priority: medium)
   - [ ] Add `USE_FOUNDRY_SCENARIOS` environment variable
   - [ ] Implement dual-path logic in `scan()`
   - [ ] Ensure backward compatibility

4. **Testing** (priority: high)
   - [ ] Unit tests for strategy_mapping
   - [ ] Integration test with real FoundryScenario
   - [ ] Verify output format matches

## Design Decisions Log

| Decision | Rationale | Date | Status |
|----------|-----------|------|--------|
| Target PyRIT 0.10.0+ | Latest stable, SQLite-only | 2025-12-17 | ✅ |
| Use SQLite memory | Only option in 0.10.0+ | 2025-12-17 | ✅ |
| Use MessagePiece | PyRIT 0.10.0 renamed class | 2025-12-17 | ✅ |
| Strategy mapping layer | Decouple from PyRIT changes | 2025-12-17 | ✅ |
| Feature flag rollout | Gradual migration, A/B test | 2025-12-17 | ⬜ |
| Keep XPIA custom logic | PyRIT doesn't support yet | 2025-12-18 | ✅ |
| Exclude PAIR from mapping | Not in AttackStrategy enum | 2025-12-18 | ✅ |

## Metrics

### Code Changes (Actual)
- **Files modified:** 2 (_red_team.py, progress.md)
- **Files created:** 2 (_utils/strategy_mapping.py, progress.md)
- **Lines added:** ~160
- **Lines modified:** ~8

### Test Coverage (Target)
- Unit tests: >90%
- Integration tests: >85%
- E2E scenarios: 100% of critical paths

---

**Document Owner:** Azure AI Evaluation Team  
**Last Updated:** 2025-12-18  
**Next Review:** Phase 1 completion
