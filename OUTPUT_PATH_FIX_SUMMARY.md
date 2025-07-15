# Red Team Scan Output Path Fix

## Problem Description

When running a red team scan with `output_path` specified, the interim evaluation outputs were missing from the scan folder because the `output_path` was being reused for every evaluation completion. This caused each evaluation to overwrite the previous evaluation's results, with only the last evaluation's output remaining.

## Root Cause

In the `scan` method of the `RedTeam` class (`_red_team.py`), the `output_path` parameter intended for the final aggregated results was being passed down to every individual evaluation task via the `_process_attack` method (line 3048).

```python
# BEFORE (buggy behavior)
orchestrator_tasks.append(
    self._process_attack(
        # ... other parameters ...
        output_path=output_path,  # ❌ This caused the issue
        # ... other parameters ...
    )
)
```

This meant that every evaluation task (each strategy/risk_category combination) tried to write to the same `output_path`, causing overwrites.

## Solution

Changed line 3048 in `_red_team.py` to pass `None` for `output_path` to individual evaluations:

```python
# AFTER (fixed behavior)
orchestrator_tasks.append(
    self._process_attack(
        # ... other parameters ...
        output_path=None,  # ✅ Individual evaluations create unique files
        # ... other parameters ...
    )
)
```

## How the Fix Works

1. **Individual Evaluations**: When `output_path=None` is passed to `_evaluate`, the method uses its existing logic (lines 2470-2472) to create unique filenames in the scan output directory:
   ```python
   result_filename = f"{strategy_name}_{risk_category.value}_{str(uuid.uuid4())}{RESULTS_EXT}"
   result_path = os.path.join(self.scan_output_dir, result_filename)
   ```

2. **Final Output**: The original `output_path` is still used correctly at the end of the scan for writing the final aggregated results (lines 3141-3156).

## Benefits

- ✅ **No Data Loss**: All evaluation results are preserved
- ✅ **Interim Files Available**: Each evaluation creates its own file in the scan directory
- ✅ **Final Aggregation**: The specified `output_path` is used only for final results
- ✅ **Backward Compatibility**: No API changes, existing behavior preserved

## File Structure After Fix

```
scan_output_directory/
├── baseline_violence_a1b2c3d4.json          # Individual evaluation result
├── baseline_hate_unfairness_e5f6g7h8.json   # Individual evaluation result  
├── jailbreak_violence_i9j0k1l2.json         # Individual evaluation result
├── jailbreak_hate_unfairness_m3n4o5p6.json  # Individual evaluation result
└── final_results.json                       # Copy of final results

specified_output_path.json                   # Final aggregated results
```

## Testing

Added comprehensive test `TestRedTeamOutputPath::test_output_path_not_passed_to_individual_evaluations` to verify:
- Individual evaluations receive `output_path=None`
- Unique evaluation result files are created in scan directory
- No overwrites occur
- All evaluation data is preserved

## Manual Verification

Created `manual_verification_output_path_fix.py` script that can be run without dependencies to verify the fix works correctly.

## Files Changed

1. `azure/ai/evaluation/red_team/_red_team.py` - Line 3048: Changed `output_path=output_path` to `output_path=None`
2. `tests/unittests/test_redteam/test_red_team.py` - Added test to verify the fix