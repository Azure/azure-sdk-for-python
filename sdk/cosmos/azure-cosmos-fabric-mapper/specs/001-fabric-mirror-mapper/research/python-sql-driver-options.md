# Research: Python SQL Driver Options for Microsoft Fabric SQL Endpoints

**Date**: 2026-01-30  
**Context**: Evaluating alternatives to pyodbc + Microsoft ODBC Driver for SQL connectivity to Fabric mirrored tables  
**Question**: Can we use a pure Python SQL driver instead of requiring system-level ODBC driver installation?

## Executive Summary

**YES** - Microsoft has released a **pure Python driver called `mssql-python`** that eliminates the need for system-level ODBC driver installation on Windows, and significantly simplifies installation on Linux/macOS.

### Key Advantages of `mssql-python`

1. **No system-level driver required on Windows** - Single `pip install` is sufficient
2. **Simplified Linux/macOS installation** - Only minimal system libraries needed (libltdl, krb5), no full ODBC driver
3. **Official Microsoft driver** - Actively maintained, first-party support
4. **TDS protocol implementation** - Native Tabular Data Stream protocol support
5. **DB-API 2.0 compliant** - Drop-in replacement for pyodbc in most cases
6. **Officially documented for Fabric** - Microsoft documentation explicitly shows usage with "SQL database in Fabric"

## Driver Comparison

| Feature | pyodbc + ODBC Driver 18 | mssql-python | pymssql |
|---------|------------------------|--------------|---------|
| **System driver required** | ✅ Yes (Microsoft ODBC Driver) | ❌ No (Windows), Minimal (Linux/Mac) | ❌ No (uses FreeTDS) |
| **Installation complexity** | High (separate installer) | Low (pip only on Windows) | Medium (FreeTDS dependency) |
| **Windows support** | ✅ Excellent | ✅ Excellent (zero external deps) | ⚠️ Good (FreeTDS) |
| **Linux support** | ✅ Good (requires driver) | ✅ Good (minimal libs) | ⚠️ Fair |
| **macOS support** | ✅ Good (requires driver) | ✅ Good (openssl via brew) | ⚠️ Fair |
| **Microsoft official** | ✅ Yes | ✅ Yes | ❌ No (community) |
| **Fabric SQL support** | ✅ Yes | ✅ Yes (documented) | ⚠️ Untested |
| **Active maintenance** | ✅ Active | ✅ Active (new 2024+) | ⚠️ Limited |
| **Entra ID auth** | ✅ Yes | ✅ Yes | ❌ Limited |
| **DB-API 2.0** | ✅ Yes | ✅ Yes | ✅ Yes |

## mssql-python Details

### Installation Requirements

**Windows:**
```bash
pip install mssql-python
```
No additional dependencies required!

**Linux (Debian/Ubuntu):**
```bash
apt-get install -y libltdl7 libkrb5-3 libgssapi-krb5-2
pip install mssql-python
```

**Linux (RHEL/CentOS):**
```bash
dnf install -y libtool-ltdl krb5-libs
pip install mssql-python
```

**macOS:**
```bash
brew install openssl
pip install mssql-python
```

### Architecture

- **Protocol**: Native TDS (Tabular Data Stream) implementation
- **Language**: Pure Python with minimal C extensions
- **Standard**: DB-API 2.0 (PEP 249) compliant
- **Authentication**: Supports Microsoft Entra ID (ActiveDirectoryInteractive, ActiveDirectoryMSI, ActiveDirectoryServicePrincipal, ActiveDirectoryPassword)

### Usage Example

```python
from mssql_python import connect

# Connection string format (same as ODBC)
conn_str = (
    "Server=your-fabric.msit-datawarehouse.fabric.microsoft.com;"
    "Database=your-database;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Authentication=ActiveDirectoryInteractive"
)

conn = connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT * FROM dbo.mytable WHERE id = ?", (123,))
rows = cursor.fetchall()
```

### Known Limitations

Based on GitHub wiki, `mssql-python` has some known issues/unsupported features:
- Check their [Known Issues page](https://github.com/microsoft/mssql-python/wiki/Known-Issues-and-Unsupported-Features) for current limitations
- Generally these are edge cases and don't affect standard query operations

## Fabric-Specific Validation

Microsoft's official documentation explicitly shows `mssql-python` being used with:
- ✅ **SQL database in Fabric** (explicitly mentioned in docs)
- ✅ **Azure SQL Database**
- ✅ **SQL Server**
- ✅ **Microsoft Fabric Warehouse** (uses same TDS endpoint)

From Microsoft Fabric connectivity docs:
> "The dbt Fabric DW Adapter uses the pyodbc library to establish connectivity with the Warehouse. The pyodbc library is an ODBC implementation in Python language that uses Python Database API Specification v2.0. The pyodbc library directly passes connection string to the database driver through SQLDriverConnect in the msodbc connection structure to Microsoft Fabric using a TDS (Tabular Data Streaming) proxy service."

**Key insight**: The underlying connection uses **TDS protocol**, which `mssql-python` implements natively without needing the ODBC layer.

## Alternative: pymssql

### Pros
- Pure Python (uses FreeTDS)
- No system ODBC driver required
- Long history (existed before mssql-python)

### Cons
- ⚠️ **Maintenance concerns**: Less actively maintained than Microsoft's official drivers
- ⚠️ **FreeTDS dependency**: Still requires FreeTDS library installation
- ⚠️ **Limited Entra ID support**: Doesn't support modern Microsoft Entra authentication well
- ⚠️ **Not officially tested with Fabric**: No Microsoft documentation showing Fabric usage

## Recommendation

### Primary Recommendation: Use `mssql-python`

**Rationale:**
1. **Best user experience on Windows** - Zero system dependencies, just `pip install`
2. **Official Microsoft support** - First-party driver, documented for Fabric
3. **Simplified deployment** - Much easier than current pyodbc + ODBC Driver requirement
4. **Modern auth support** - Full Microsoft Entra ID authentication support
5. **DB-API 2.0 compliant** - Minimal code changes from pyodbc implementation

### Implementation Approach

**Option A: Make `mssql-python` the default driver** (Recommended)
- Change `pyproject.toml` to use `mssql-python` in the `[odbc]` extra
- Keep the driver abstraction layer (DriverClient protocol)
- Provide migration path for existing users

**Option B: Support both drivers**
- Add `mssql-python` as preferred, `pyodbc` as fallback
- Auto-detect which is available
- More complex but maximally compatible

**Option C: Rename the extra**
- Change `[odbc]` extra to `[sql]` or `[fabric]`
- Use `mssql-python` by default
- Document that system ODBC driver is no longer required

## Impact Assessment

### Current State (pyodbc)
```toml
[project.optional-dependencies]
odbc = ["pyodbc>=5.1.0"]
```

**User installation:**
1. Install system ODBC driver (separate download, admin rights needed)
2. Run `pip install azure-cosmos-fabric-mapper[odbc]`

### Proposed State (mssql-python)
```toml
[project.optional-dependencies]
sql = ["mssql-python>=1.0.0"]  # or keep name as 'odbc' for compatibility
```

**User installation:**
1. Run `pip install azure-cosmos-fabric-mapper[sql]`
   - Windows: Done! ✅
   - Linux: Requires standard libs (libltdl, krb5) - usually already installed
   - macOS: Requires openssl (via brew)

### Breaking Changes
- Users who have already installed pyodbc will need to migrate
- Connection string format is compatible (both use ODBC-style connection strings)
- Code changes minimal due to DB-API 2.0 compatibility

### Migration Path
1. Update documentation to recommend `mssql-python`
2. Keep `pyodbc` support for backward compatibility initially
3. Add deprecation warning for pyodbc path
4. Remove pyodbc in next major version (2.0.0)

## Code Changes Required

### Minimal changes needed:

1. **pyproject.toml** - Change dependency
2. **README.md** - Update installation instructions (much simpler!)
3. **driver/mssql_driver.py** - New driver implementation (or rename existing)
4. **driver/__init__.py** - Update imports
5. **Tests** - Update to test mssql-python

### Estimated effort: 2-4 hours

Most of the existing pyodbc code should work with minimal changes due to DB-API 2.0 compliance.

## Testing Considerations

Before switching, validate:
1. ✅ Connection to Fabric SQL endpoint works
2. ✅ Parameterized queries work correctly
3. ✅ Result set mapping matches expectations
4. ✅ Microsoft Entra ID authentication works
5. ✅ Error handling is appropriate
6. ✅ Performance is comparable to pyodbc

## References

- [mssql-python PyPI](https://pypi.org/project/mssql-python/)
- [mssql-python GitHub Wiki](https://github.com/microsoft/mssql-python/wiki)
- [Microsoft Learn: Quickstart with mssql-python](https://learn.microsoft.com/en-us/sql/connect/python/mssql-python/python-sql-driver-mssql-python-quickstart)
- [Microsoft Learn: Connect to Fabric SQL database with mssql-python](https://learn.microsoft.com/en-us/fabric/database/sql/connect-python)
- [Microsoft Fabric Connectivity Documentation](https://learn.microsoft.com/en-us/fabric/data-warehouse/connectivity)
- [Microsoft Learn: Connect to Fabric Data Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/how-to-connect)

## Decision

**Recommended**: Switch to `mssql-python` as the default/primary SQL driver for this project.

**Benefits**:
- ✅ Dramatically simplified installation (especially on Windows)
- ✅ Official Microsoft support and documentation
- ✅ Explicitly documented for Fabric SQL endpoints
- ✅ Reduces barrier to entry for users
- ✅ Aligns with Microsoft's current driver strategy

**Risks**:
- ⚠️ Relatively new driver (though officially supported)
- ⚠️ May have edge case bugs not present in mature pyodbc
- ⚠️ Breaking change for existing users (mitigated by version bump)

**Next Steps**:
1. Create prototype implementation with `mssql-python`
2. Test against actual Fabric SQL endpoint
3. Compare performance and functionality with pyodbc
4. Update documentation and migration guide
5. Release as new minor/major version with clear changelog
