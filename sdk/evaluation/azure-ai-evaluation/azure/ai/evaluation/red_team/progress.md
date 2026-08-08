# PyRIT FoundryScenario Integration - Progress Tracker

**Last Updated:** 2025-12-17  
**Current Phase:** Planning Complete  
**Next Milestone:** Phase 1 Implementation Start

## Executive Summary

This document tracks the progress of integrating PyRIT's FoundryScenario into Azure AI Evaluation's red teaming framework. The integration targets PyRIT 0.10.0, which removed DuckDB support in favor of SQLite as the sole memory backend.

## Design Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| Target PyRIT 0.10.0+ | Latest stable version with SQLite-only backend | 2025-12-17 |
| Use SQLite memory | Only option in PyRIT 0.10.0+ (DuckDB removed) | 2025-12-17 |
| Integrate FoundryScenario | Leverage PyRIT's scenario framework for structured attacks | 2025-12-17 |
| Maintain backward compatibility | Preserve existing red team API surface | 2025-12-17 |
| Store DB in output directory | Co-locate memory with scan results | 2025-12-17 |

## Phase Progress

### Phase 0: Planning ✅ (Completed 2025-12-17)

- [x] Research PyRIT 0.10.0 changes
- [x] Identify DuckDB removal and SQLite migration
- [x] Document breaking changes in current codebase
- [x] Define technical specification
- [x] Create implementation roadmap

### Phase 1: Implementation ⬜ (Week 1-2)

- [ ] Update `_red_team.py` to use SQLite initialization
- [ ] Create `_foundry_scenario.py` implementation
- [ ] Create `_scenario_manager.py` for lifecycle management
- [ ] Integrate with `_orchestrator_manager.py`
- [ ] Update imports and dependencies

### Phase 2: Testing & Validation ⬜ (Week 3)

- [ ] Write unit tests for new components
- [ ] Create integration tests
- [ ] Run end-to-end scenario tests
- [ ] Performance benchmarking
- [ ] Security review

### Phase 3: Documentation & Release ⬜ (Week 4)

- [ ] API documentation
- [ ] Migration guide
- [ ] Sample scenarios
- [ ] Code review
- [ ] Release preparation

## Current Blockers/Challenges

1. **No blockers at this time** - Planning phase complete

2. **Dependencies:**
   - Requires PyRIT >= 0.10.0
   - Must coordinate with PyRIT team for scenario API stability

3. **Testing Challenges:**
   - Need comprehensive scenario coverage
   - Must validate memory persistence across sessions
   - Performance testing with large scenario sets

4. **Breaking Change in PyRIT 0.10.0:**
   - **Issue:** Current code uses `initialize_pyrit(memory_db_type=DUCK_DB)` which no longer exists
   - **Location:** `_red_team.py` line ~222
   - **Fix Required:** Change to `initialize_pyrit(memory_db_type=SQLITE, memory_db_path=db_path)`
   - **Impact:** High - must be addressed before Phase 1 implementation

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking changes in PyRIT 0.10.0+ | Medium | High | Pin PyRIT version, comprehensive testing |
| Performance degradation with SQLite | Low | Medium | Benchmark and optimize queries |
| Backward compatibility issues | Low | High | Maintain existing API surface |
| Memory persistence issues | Low | Medium | Thorough integration testing |

## Key Metrics

### Code Changes (Estimated)
- New files: 2 (`_foundry_scenario.py`, `_scenario_manager.py`)
- Modified files: 2 (`_red_team.py`, `_orchestrator_manager.py`)
- Lines of code: ~500-800 new, ~50-100 modified

### Test Coverage Goals
- Unit test coverage: >90%
- Integration test coverage: >85%
- E2E scenario coverage: 100% of critical paths

### Performance Targets
- SQLite initialization: <100ms
- Scenario execution: No regression vs. current implementation
- Memory query latency: <50ms for typical queries

## Timeline

| Phase | Start Date | End Date | Status |
|-------|------------|----------|--------|
| Phase 0: Planning | 2025-12-10 | 2025-12-17 | ✅ Complete |
| Phase 1: Implementation | TBD | TBD | ⬜ Not Started |
| Phase 2: Testing | TBD | TBD | ⬜ Not Started |
| Phase 3: Documentation | TBD | TBD | ⬜ Not Started |

## Next Steps

1. **Immediate (Week 1):**
   - Fix breaking change in `_red_team.py` (DUCK_DB → SQLITE)
   - Set up development environment with PyRIT 0.10.0
   - Begin `_foundry_scenario.py` implementation

2. **Short-term (Week 2):**
   - Complete core implementation
   - Begin unit testing
   - Integration with orchestrator manager

3. **Medium-term (Week 3-4):**
   - Comprehensive testing
   - Documentation
   - Code review and release preparation

## References

- [PyRIT 0.10.0 Release Notes](https://github.com/Azure/PyRIT/releases)
- [Technical Specification](spec.md)
- [Azure AI Evaluation Red Team Documentation](../../README.md)

---

**Document Owner:** Azure AI Evaluation Team  
**Last Review:** 2025-12-17  
**Next Review:** TBD (Phase 1 start)
