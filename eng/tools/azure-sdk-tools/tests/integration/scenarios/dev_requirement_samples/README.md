# Summary

All three of these requirements files are intended to be "in context" of the sdk/core/azure-core package. The requirements files within this package are used to verify
the relative dependency replacement that occurs during CI builds.

Multiple tox environments cannot build the same relative dependency, python chokes on itself.