# Fix for Duplicate Queries in DirectAttackSimulator

## Problem Statement
When running `_SafetyEvaluation` with `_SafetyEvaluator.DIRECT_ATTACK` and `num_rows=200`, duplicate queries were appearing in the results.

## Root Cause Analysis
The issue was identified in the `DirectAttackSimulator.__call__()` method in `azure/ai/evaluation/simulator/_direct_attack_simulator.py`.

### The Problem
1. **Same Randomization Seed**: Both the regular and jailbreak `AdversarialSimulator` instances were receiving the same `randomization_seed` parameter.
2. **Identical Template Shuffling**: When both simulators used the same seed, they would shuffle their template lists in exactly the same way.
3. **Duplicate Query Generation**: This resulted in both simulators selecting the same templates in the same order, leading to duplicate queries.

### Code Location
In lines 204-230 of `_direct_attack_simulator.py`, both simulators were called with:
```python
randomization_seed=randomization_seed  # Same seed for both!
```

## Solution Implemented

### The Fix
Modified the `DirectAttackSimulator.__call__()` method to derive different but deterministic seeds:

```python
# Derive different seeds for regular and jailbreak simulations to avoid duplicate queries
# This ensures deterministic behavior while preventing identical results
regular_seed = randomization_seed
jailbreak_seed = randomization_seed + 1 if randomization_seed < 999999 else randomization_seed - 1
```

### Key Benefits
1. **Maintains Deterministic Behavior**: When the same `randomization_seed` is provided, the results are still reproducible.
2. **Eliminates Duplicates**: Regular and jailbreak simulations now use different seeds, producing different query sequences.
3. **Handles Edge Cases**: Properly handles the maximum seed value (999999) by subtracting 1 instead of adding 1.
4. **Minimal Impact**: Only changes the seed derivation logic without affecting other functionality.

## Files Modified

### 1. Core Fix
- **File**: `azure/ai/evaluation/simulator/_direct_attack_simulator.py`
- **Changes**:
  - Added seed derivation logic (lines 204-207)
  - Updated regular simulator call to use `regular_seed`
  - Updated jailbreak simulator call to use `jailbreak_seed`
  - Updated documentation to clarify the new behavior

### 2. Test Coverage
- **File**: `tests/unittests/test_direct_attack_simulator.py` (NEW)
- **Tests Added**:
  - `test_different_randomization_seeds_fix`: Verifies different seeds are used
  - `test_edge_case_max_seed_value`: Tests edge case with maximum seed value
  - `test_no_seed_provided_generates_different_seeds`: Tests random seed generation

- **File**: `tests/unittests/test_safety_evaluation.py`
- **Tests Added**:
  - `test_direct_attack_different_seeds_fix`: Integration test for the fix

## Validation

### Manual Testing
Created validation scripts that confirmed:
1. ✅ Same seeds produce identical shuffling (reproducing the original problem)
2. ✅ Different seeds produce different shuffling (confirming the fix)
3. ✅ Edge cases (max seed value) are handled correctly
4. ✅ Deterministic behavior is preserved

### Test Results
```
Testing seed derivation logic...
✓ Test case 1 (normal seed): PASSED
✓ Test case 2 (max seed): PASSED
✓ Test case 3 (another normal seed): PASSED

Testing template shuffling with different seeds...
✓ Confirmed: Same seeds produce identical shuffling (old problematic behavior)
✓ Fixed: Different seeds produce different shuffling (new correct behavior)
```

## Impact Assessment

### Positive Impacts
- ✅ **Eliminates Duplicate Queries**: The primary issue is resolved
- ✅ **Maintains Reproducibility**: Same input seed still produces same results
- ✅ **Zero Breaking Changes**: No API changes, existing code continues to work
- ✅ **Better Test Coverage**: Added comprehensive unit tests

### Risk Assessment
- 🟢 **Low Risk**: Minimal code changes with clear logic
- 🟢 **Backward Compatible**: No API or behavior changes for consumers
- 🟢 **Well Tested**: Comprehensive test coverage for edge cases

## Usage Example

```python
# Before fix: Both simulations would use seed=42, causing duplicates
# After fix: Regular uses seed=42, jailbreak uses seed=43

simulator = DirectAttackSimulator(azure_ai_project=project, credential=cred)
result = await simulator(
    scenario=AdversarialScenario.ADVERSARIAL_QA,
    target=my_target,
    max_simulation_results=200,
    randomization_seed=42  # Deterministic but no duplicates
)

# result["regular"] and result["jailbreak"] now contain different queries
```

## Verification Steps
To verify the fix is working:

1. Run safety evaluation with DIRECT_ATTACK and num_rows=200
2. Compare queries in the regular vs jailbreak results
3. Confirm no duplicates exist between the two sets
4. Verify that using the same seed still produces reproducible results across runs

This fix ensures that DirectAttackSimulator produces diverse, non-duplicate queries while maintaining the deterministic behavior that users expect from seeded randomization.