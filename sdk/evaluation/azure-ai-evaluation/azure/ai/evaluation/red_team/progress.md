# PyRIT FoundryScenario Integration - Progress Tracking

**Last Updated:** December 17, 2024

---

## 📊 Current Status

**Phase:** Design Complete → Implementation Pending

We have completed comprehensive planning and technical design for integrating PyRIT's FoundryScenario system into the azure-sdk-for-python red team module. The implementation phase has not yet begun, with code changes scheduled to be rolled out in phases using a feature flag approach.

**Overall Progress:** Design 100% | Implementation 0%

---

## 🎯 Approach

### Integration Strategy

We are integrating PyRIT's FoundryScenario system to modernize our red team attack execution framework. This integration will:

1. **Minimize Breaking Changes:** Leverage PyRIT's stable FoundryScenario API to reduce the impact of PyRIT version updates
2. **Enable Rapid Expansion:** Simplify the process of adding new attack strategies by delegating to PyRIT's framework
3. **Reduce Custom Code:** Eliminate custom orchestration code in favor of PyRIT's battle-tested implementations
4. **Improve Maintainability:** Centralize attack execution logic in PyRIT while keeping strategy mapping in azure-sdk-for-python

### Key Design Principles

- **Phased Rollout:** Use feature flags to enable gradual migration from current orchestrator to FoundryScenario
- **Backward Compatibility:** Maintain existing API surface while modernizing internal implementation
- **Strategy Mapping Layer:** Create a clean mapping between AttackStrategy enum and FoundryScenario configurations
- **RAI Service Integration:** Preserve existing RAI service scorer integration for result evaluation
- **Memory Label Preservation:** Use PyRIT's memory labels to maintain conversation context across turns

---

## ✅ Completed Steps

### 1. Technical Specification (spec.md)
- [x] Created comprehensive technical specification document
- [x] Documented current architecture and identified pain points
- [x] Outlined integration approach with detailed rationale
- [x] Specified strategy mapping for all attack types
- [x] Defined feature flag mechanism for gradual rollout

### 2. Architecture Analysis
- [x] Analyzed current `_orchestrator_manager.py` implementation
- [x] Identified pain points with direct PyRIT orchestrator usage
- [x] Documented challenges with version compatibility
- [x] Mapped existing attack strategies to PyRIT capabilities

### 3. Strategy Mapping Design
- [x] Designed comprehensive strategy mapping layer
- [x] Mapped all 28 attack strategies to FoundryScenario configurations
- [x] Defined converter-based vs. multi-turn strategy categorization
- [x] Created fallback mechanism for unmapped strategies
- [x] Documented strategy composition support

### 4. RAI Service Scorer Integration
- [x] Planned integration with existing `AzureRAIServiceTrueFalseScorer`
- [x] Designed scorer configuration within FoundryScenario
- [x] Maintained compatibility with current evaluation pipeline
- [x] Preserved existing RAI service endpoint usage

### 5. Context Preservation Design
- [x] Designed memory label usage for conversation tracking
- [x] Planned strategy/risk category tagging in PyRIT memory
- [x] Ensured context preservation across multi-turn conversations
- [x] Designed result extraction from PyRIT memory system

### 6. XPIA Support Planning
- [x] Created feature request options for Cross-domain Prompt Injection Attacks
- [x] Documented two approach options (custom vs. PyRIT native)
- [x] Identified dependencies on PyRIT FoundryScenario enhancements
- [x] Planned incremental implementation path

---

## ⬜ Pending Steps

### Phase 1: Core Infrastructure (Not Started)
- [ ] Implement `_strategy_mapper.py` module
  - [ ] Create `StrategyMapper` class
  - [ ] Implement strategy-to-FoundryScenario mapping logic
  - [ ] Add converter selection logic
  - [ ] Implement multi-turn strategy configuration
- [ ] Create `_foundry_orchestrator_manager.py` module
  - [ ] Implement FoundryScenario initialization
  - [ ] Add RAI scorer integration
  - [ ] Implement memory label configuration
  - [ ] Create result extraction logic
- [ ] Add feature flag infrastructure
  - [ ] Define `USE_FOUNDRY_SCENARIO` environment variable
  - [ ] Implement feature flag checking in `_red_team.py`
  - [ ] Add logging for feature flag state

### Phase 2: Integration (Not Started)
- [ ] Modify `_red_team.py` to support dual execution paths
  - [ ] Add conditional logic for Foundry vs. legacy orchestrator
  - [ ] Ensure consistent result format across both paths
  - [ ] Preserve existing API surface
- [ ] Update `_orchestrator_manager.py`
  - [ ] Add delegation to FoundryScenario when flag enabled
  - [ ] Maintain backward compatibility with existing code
  - [ ] Preserve retry logic and error handling

### Phase 3: Testing & Validation (Not Started)
- [ ] Create unit tests for `StrategyMapper`
- [ ] Create integration tests for `_foundry_orchestrator_manager.py`
- [ ] Add feature flag toggle tests
- [ ] Validate all 28 attack strategies work with FoundryScenario
- [ ] Test multi-turn conversations (Crescendo, MultiTurn, Jailbreak)
- [ ] Validate RAI scorer integration
- [ ] Test memory label preservation

### Phase 4: Documentation & Migration (Not Started)
- [ ] Update module documentation
- [ ] Create migration guide for users
- [ ] Document feature flag usage
- [ ] Add troubleshooting section
- [ ] Create examples for new FoundryScenario-based execution

### Phase 5: Production Rollout (Not Started)
- [ ] Enable feature flag in development environment
- [ ] Monitor for issues and regressions
- [ ] Gradual rollout to production
- [ ] Collect metrics on performance and reliability
- [ ] Remove legacy orchestrator code once stable
- [ ] Clean up feature flag infrastructure

---

## 🚧 Current Blockers/Challenges

### Technical Decisions Needed

1. **Feature Flag Default State**
   - Decision needed: Should `USE_FOUNDRY_SCENARIO` default to enabled or disabled?
   - Recommendation: Default to disabled initially, enable after validation
   - Impact: Affects rollout timeline and risk level

2. **Backward Compatibility Scope**
   - Decision needed: How long to maintain dual execution paths?
   - Recommendation: At least 2 release cycles before removing legacy code
   - Impact: Affects code maintenance burden

3. **XPIA Implementation Approach**
   - Decision needed: Custom implementation vs. waiting for PyRIT native support?
   - Recommendation: Start with custom, migrate when PyRIT adds native support
   - Impact: Affects XPIA feature timeline and maintenance complexity

### External Dependencies

1. **PyRIT FoundryScenario Stability**
   - Status: Need to validate FoundryScenario API stability in PyRIT
   - Blocker: Low - API appears stable but needs verification
   - Action: Review PyRIT release notes and API contracts

2. **PyRIT XPIA Support**
   - Status: XPIA not natively supported in FoundryScenario yet
   - Blocker: Medium - Blocks full strategy migration
   - Action: Either implement custom XPIA wrapper or file PyRIT feature request

### Resource Constraints

1. **Implementation Bandwidth**
   - Current: No implementation resources allocated
   - Impact: Implementation timeline uncertain
   - Action: Allocate engineering resources for Phase 1

2. **Testing Infrastructure**
   - Current: Need to determine test coverage requirements
   - Impact: Affects validation timeline
   - Action: Define test plan and coverage targets

---

## 🎬 Next Actions

### Immediate (Week 1-2)

1. **Validate PyRIT FoundryScenario API**
   - Review PyRIT documentation for FoundryScenario
   - Test basic FoundryScenario usage with current PyRIT version
   - Verify API stability and backward compatibility guarantees

2. **Set Up Development Environment**
   - Create feature branch for implementation
   - Set up test environment with feature flag support
   - Configure local development for rapid iteration

3. **Implement Core StrategyMapper**
   - Create `_strategy_mapper.py` module
   - Implement basic strategy-to-FoundryScenario mapping
   - Add unit tests for strategy mapping logic

### Short-term (Week 3-4)

4. **Build FoundryOrchestratorManager**
   - Implement `_foundry_orchestrator_manager.py`
   - Integrate with StrategyMapper
   - Add basic error handling and logging

5. **Integrate Feature Flag**
   - Add feature flag check in `_red_team.py`
   - Implement conditional execution path
   - Test toggle between legacy and Foundry execution

6. **Initial Integration Testing**
   - Test basic single-turn strategies with FoundryScenario
   - Validate result format compatibility
   - Verify RAI scorer integration works

### Medium-term (Month 2)

7. **Complete All Strategy Mappings**
   - Implement and test all 28 attack strategies
   - Validate multi-turn conversation strategies
   - Test strategy composition support

8. **Comprehensive Testing**
   - Unit test coverage for all new modules
   - Integration tests for full execution flow
   - Performance testing and optimization

9. **Documentation & Examples**
   - Update module documentation
   - Create usage examples
   - Write migration guide

### Long-term (Month 3+)

10. **Production Rollout**
    - Enable feature flag in staging environment
    - Monitor metrics and error rates
    - Gradual rollout to production
    - Deprecate legacy orchestrator code

---

## 📝 Notes

### Design Artifacts

- **Technical Specification:** `spec.md` (referenced in problem statement, contains detailed design)
- **Current Implementation:** `_orchestrator_manager.py` (legacy, to be replaced)
- **Target Architecture:** FoundryScenario-based execution with strategy mapping layer

### Key Architectural Components

1. **StrategyMapper:** Maps AttackStrategy enum to FoundryScenario configurations
2. **FoundryOrchestratorManager:** Manages FoundryScenario lifecycle and execution
3. **Feature Flag:** `USE_FOUNDRY_SCENARIO` environment variable for gradual rollout
4. **Memory Labels:** PyRIT memory system tags for context preservation
5. **RAI Scorer Integration:** Existing AzureRAIServiceTrueFalseScorer preserved

### Success Criteria

- ✅ All 28 attack strategies work with FoundryScenario
- ✅ Zero breaking changes to public API
- ✅ Feature flag enables safe rollout
- ✅ RAI service integration maintained
- ✅ Performance on par with or better than legacy implementation
- ✅ Reduced maintenance burden from PyRIT updates

---

## 📞 Contact & Collaboration

For questions or to contribute to this implementation:

1. Review the technical specification (`spec.md`) for detailed design decisions
2. Check this progress document for current status
3. Coordinate with the team before starting implementation work
4. Update this document when completing major milestones

---

**Document Version:** 1.0  
**Created:** December 17, 2024  
**Next Review:** TBD (after Phase 1 completion)
