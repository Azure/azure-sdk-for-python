# Release History

## 1.0.0 (2024-07-04)

### Other Changes

  - First GA

## 1.0.0b2 (2024-06-21)

### Features Added

  - Added operation AutonomousDatabasesOperations.begin_restore
  - Added operation AutonomousDatabasesOperations.begin_shrink
  - Added operation group SystemVersionsOperations
  - Model AutonomousDatabaseBackupProperties has a new parameter autonomous_database_ocid
  - Model AutonomousDatabaseBackupProperties has a new parameter backup_type
  - Model AutonomousDatabaseBackupProperties has a new parameter database_size_in_tbs
  - Model AutonomousDatabaseBackupProperties has a new parameter size_in_tbs
  - Model AutonomousDatabaseBackupProperties has a new parameter time_started
  - Model AutonomousDatabaseBaseProperties has a new parameter long_term_backup_schedule
  - Model AutonomousDatabaseBaseProperties has a new parameter next_long_term_backup_time_stamp
  - Model AutonomousDatabaseCloneProperties has a new parameter long_term_backup_schedule
  - Model AutonomousDatabaseCloneProperties has a new parameter next_long_term_backup_time_stamp
  - Model AutonomousDatabaseProperties has a new parameter long_term_backup_schedule
  - Model AutonomousDatabaseProperties has a new parameter next_long_term_backup_time_stamp
  - Model AutonomousDatabaseUpdateProperties has a new parameter long_term_backup_schedule

### Breaking Changes

  - Model AutonomousDatabaseBackupProperties no longer has parameter autonomous_database_id
  - Model AutonomousDatabaseBackupProperties no longer has parameter database_size_in_t_bs
  - Model AutonomousDatabaseBackupProperties no longer has parameter size_in_t_bs
  - Model AutonomousDatabaseBackupProperties no longer has parameter type

## 1.0.0b1 (2024-05-27)

* Initial Release
