# Files That Need Hand-Crafted Test Plans

These source files defeated automated LLM test generation and need manual test planning.

## `azure/ai/ml/operations/_job_operations.py`
- **Gap size**: 377 missing lines / 313 uncovered branches (largest in operations layer)
- **Why it's hard**:
  1. **Deep internal wiring** — `_resolve_arm_id_*` methods traverse complex job graphs (PipelineJob, SweepJob, SparkJob). Triggering these branches requires deeply nested, valid job objects with registered environments, datasets, and compute targets.
  2. **Singularity/VirtualCluster compute paths** — `_try_get_compute_arm_id` has branches for Singularity IDs, full names, short names, PipelineInput, data binding expressions. Requires specific compute infra that doesn't exist in test workspace.
  3. **Post-execution code paths** — `download()`, `_get_named_output_uri()`, `stream()` require already-completed jobs with real outputs. Can't test download without first running a job to completion (5-30 min).
- **What would work**: Use existing YAML configs from `tests/test_configs/`, pre-create jobs before testing download/stream, accept some paths (Singularity) need unit tests with mocks.
- **LLM behavior**: Wrote no-op scaffolds (`try/except Exception: pass`) gated behind `is_live()`. Fix loop ran for 7+ hours retrying.
