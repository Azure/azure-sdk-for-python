# Release History

## 1.0.0b1 (Unreleased)

### Breaking Changes

- The `synthetic` namespace has been renamed to `simulator`, and sub-namespaces under this module have been removed
- The `evaluate` and `evaluators` namespaces have been removed, and everything previously exposed in those modules has been added to the root namespace `azure.ai.evaluation`  
- The parameter name `project_scope` in content safety evaluators have been renamed to `azure_ai_project` for consistency with evaluate API and simulators.
- Updated the parameter names for `question` and `answer` in built-in evaluators to more generic terms: `query` and `response`.
- `data` and `evaluators` are now required keywords in `evaluate`.


### Features Added

- First preview
- This package is port of `promptflow-evals`. New features will be added only to this package moving forward.
