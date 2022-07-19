# Release History

## 1.0.0b5 (2022-07-19)

**Features**

  - Added operation ExperimentsOperations.cancel
  - Added operation ExperimentsOperations.create_or_update
  - Model CapabilityType has a new parameter kind
  - Model CapabilityType has a new parameter runtime_properties

**Breaking changes**

  - Removed operation ExperimentsOperations.begin_cancel
  - Removed operation ExperimentsOperations.begin_create_or_update

## 1.0.0b4 (2022-06-28)

**Features**

  - Model ActionStatus has a new parameter action_id
  - Model ActionStatus has a new parameter action_name
  - Model BranchStatus has a new parameter branch_id
  - Model BranchStatus has a new parameter branch_name
  - Model ExperimentExecutionActionTargetDetailsProperties has a new parameter target_completed_time
  - Model ExperimentExecutionActionTargetDetailsProperties has a new parameter target_failed_time
  - Model ExperimentExecutionDetails has a new parameter created_date_time
  - Model ExperimentExecutionDetails has a new parameter last_action_date_time
  - Model ExperimentExecutionDetails has a new parameter start_date_time
  - Model ExperimentExecutionDetails has a new parameter stop_date_time
  - Model StepStatus has a new parameter step_id
  - Model StepStatus has a new parameter step_name

**Breaking changes**

  - Model ActionStatus no longer has parameter id
  - Model ActionStatus no longer has parameter name
  - Model BranchStatus no longer has parameter id
  - Model BranchStatus no longer has parameter name
  - Model ExperimentExecutionActionTargetDetailsProperties no longer has parameter completed_date_utc
  - Model ExperimentExecutionActionTargetDetailsProperties no longer has parameter failed_date_utc
  - Model ExperimentExecutionDetails no longer has parameter created_date_utc
  - Model ExperimentExecutionDetails no longer has parameter last_action_date_utc
  - Model ExperimentExecutionDetails no longer has parameter start_date_utc
  - Model ExperimentExecutionDetails no longer has parameter stop_date_utc
  - Model StepStatus no longer has parameter id
  - Model StepStatus no longer has parameter name

## 1.0.0b3 (2022-05-07)

**Features**

  - Model ActionStatus has a new parameter end_time
  - Model ActionStatus has a new parameter start_time

## 1.0.0b2 (2021-10-25)

**Features**

  - Modified client name

## 1.0.0b1 (2021-10-21)

* Initial Release
