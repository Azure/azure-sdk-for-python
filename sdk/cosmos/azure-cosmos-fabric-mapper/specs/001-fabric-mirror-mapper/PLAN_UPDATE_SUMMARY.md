# Plan Update Summary: SQL Driver Strategy Change

**Date**: 2026-01-30  
**Branch**: 001-fabric-mirror-mapper  
**Change Type**: Strategic Architecture Update

## What Changed

Based on research into Python SQL driver options for Microsoft Fabric SQL endpoints, the implementation plan has been updated to use **`mssql-python`** as the primary driver instead of **`pyodbc`**.

## Key Findings

1. **Microsoft's new `mssql-python` driver eliminates system-level ODBC driver installation**
   - Windows: Zero system dependencies (just `pip install`)
   - Linux/macOS: Minimal system libraries (libltdl, krb5, openssl)
   - Official Microsoft driver with first-party Fabric SQL support

2. **Dramatically simplified user experience**
   - Before: Install system ODBC driver + pip install
   - After: Just pip install (on Windows)

3. **No code changes required**
   - Both drivers are DB-API 2.0 compliant
   - Same connection string format
   - Drop-in replacement for existing pyodbc code

## Files Updated

### 1. Research Documentation

- **`specs/001-fabric-mirror-mapper/research.md`**
  - Updated driver decision section
  - Added detailed comparison of mssql-python vs pyodbc vs pymssql
  - Linked to detailed research document

- **`specs/001-fabric-mirror-mapper/research/python-sql-driver-options.md`** (NEW)
  - Comprehensive driver comparison
  - Installation requirements for all platforms
  - Migration considerations
  - Testing checklist
  - Recommendation rationale

### 2. Implementation Plan

- **`specs/001-fabric-mirror-mapper/plan.md`**
  - Updated summary with driver strategy change
  - Updated Technical Context section
  - Updated Constitution Check (driver change strengthens goals)
  - Updated Project Structure (mssql_driver.py as primary)
  - Added Phase 0 completion status
  - Added migration tasks to Phase 2

### 3. Project Configuration

- **`pyproject.toml`**
  - Changed keywords from "odbc" to "sql"
  - Added `[sql]` extra with `mssql-python>=1.0.0`
  - Kept `[odbc]` extra for backward compatibility
  - Added explanatory comments

### 4. User Documentation

- **`README.md`**
  - Complete installation section rewrite
  - Recommended installation now uses `[sql]` extra
  - Added migration guide from pyodbc to mssql-python
  - Updated architecture diagram
  - Added driver strategy explanation
  - Kept pyodbc instructions for legacy users

## Impact Assessment

### Benefits

✅ **Dramatically simplified installation**
- Windows users: 1 command instead of 2+ separate installers
- No admin rights needed for ODBC driver installation
- Fewer support issues related to driver installation

✅ **Better user onboarding**
- Lower barrier to entry
- Faster time-to-first-query
- Clearer getting-started experience

✅ **Official Microsoft support**
- First-party driver for Fabric SQL
- Documented in Microsoft Learn
- Active maintenance and updates

✅ **Easier deployment**
- Simpler Docker containers
- Easier CI/CD pipelines
- Better cloud deployment story

### Risks (Mitigated)

⚠️ **Breaking change for existing users**
- Mitigation: Keep `[odbc]` extra for backward compatibility
- Mitigation: Provide clear migration guide
- Mitigation: No code changes required (DB-API 2.0 compliance)

⚠️ **Newer driver may have undiscovered issues**
- Mitigation: Microsoft official support
- Mitigation: Explicitly documented for Fabric SQL
- Mitigation: Can fall back to pyodbc if needed

## Next Steps

### Immediate (Documentation)
✅ Research completed
✅ Plan updated
✅ pyproject.toml updated
✅ README updated with migration guide

### Short-term (Implementation)
⏭️ Create `src/azure_cosmos_fabric_mapper/driver/mssql_driver.py`
⏭️ Add tests for mssql-python driver
⏭️ Test against actual Fabric SQL endpoint
⏭️ Validate performance parity with pyodbc

### Medium-term (Release)
⏭️ Update CHANGELOG.md with driver strategy change
⏭️ Release as new minor version (0.2.0 or 1.0.0)
⏭️ Announce change in release notes
⏭️ Monitor for any migration issues

## Compatibility Matrix

| Installation Method | System Driver Required | Supported Platforms |
|-------------------|------------------------|-------------------|
| `pip install azure-cosmos-fabric-mapper[sql]` | ❌ No (Windows)<br>⚠️ Minimal libs (Linux/Mac) | Windows, Linux, macOS |
| `pip install azure-cosmos-fabric-mapper[odbc]` | ✅ Yes (ODBC Driver 18) | Windows, Linux, macOS |

## References

- Research document: [specs/001-fabric-mirror-mapper/research/python-sql-driver-options.md](specs/001-fabric-mirror-mapper/research/python-sql-driver-options.md)
- Microsoft Learn: [Quickstart with mssql-python](https://learn.microsoft.com/en-us/sql/connect/python/mssql-python/python-sql-driver-mssql-python-quickstart)
- Microsoft Learn: [Connect to Fabric SQL with mssql-python](https://learn.microsoft.com/en-us/fabric/database/sql/connect-python)
- PyPI: [mssql-python](https://pypi.org/project/mssql-python/)
- GitHub: [microsoft/mssql-python](https://github.com/microsoft/mssql-python)

## Questions & Answers

**Q: Do I need to change my code?**  
A: No! Both drivers use DB-API 2.0 interface. Your existing connection code works as-is.

**Q: What if I want to keep using pyodbc?**  
A: Continue using `[odbc]` extra. Both drivers will be supported.

**Q: Is mssql-python production-ready?**  
A: Yes. It's an official Microsoft driver, actively maintained, and explicitly documented for Fabric SQL.

**Q: What about performance?**  
A: Both drivers use the same TDS protocol. Performance should be comparable. Testing required for validation.

**Q: Can I use both drivers in the same project?**  
A: Technically yes (they're separate packages), but choose one for consistency. The mapper abstraction layer supports both.
