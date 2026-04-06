# Description

Fixes a bug where Crescendo and MultiTurn attack strategies produce output items
identical to their baseline counterparts. Multi-turn conversations execute correctly,
but the result assembly pipeline conflates all conversations across strategies because
they share the same JSONL data file.

## Root Cause

The Foundry execution path generates a single JSONL per risk category and assigns the
same file to ALL strategies in red_team_info. When ResultProcessor reads this file for
each strategy, every conversation is duplicated and labeled with whichever strategy is
currently being processed.

The legacy orchestrator path (<=1.14.0) avoided this by generating a separate UUID-based
JSONL file per (strategy, risk_category) pair.

## Fix

Follows the legacy pattern: after FoundryResultProcessor writes the combined JSONL, a new
`_split_jsonl_by_strategy()` method partitions entries by their `attack_strategy` field
(PyRIT class name) into per-strategy files.

### Changes
- **`_execution_manager.py`**: Add `_split_jsonl_by_strategy()` and `_PYRIT_NAME_TO_STRATEGY_VALUE` mapping; update `_group_results_by_strategy()` to use per-strategy file paths
- **`test_foundry.py`**: Update 5 existing tests for new method signature; add 2 new tests

# All SDK Contribution checklist:
- [x] **The pull request does not introduce breaking changes**
- [ ] **CHANGELOG is updated for new features, bug fixes or other significant changes.**
- [x] **I have read the contribution guidelines**

### Testing
- [x] Pull request includes test coverage for the included changes.
