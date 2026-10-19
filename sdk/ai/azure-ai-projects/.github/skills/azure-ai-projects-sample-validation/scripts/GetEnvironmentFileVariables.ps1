# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$EnvFile,
    [string]$PythonExecutable,
    [string]$PackageRoot,
    [switch]$IncludeValues
)

$ErrorActionPreference = "Stop"
if ($PackageRoot) {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path -LiteralPath $PackageRoot).Path).FullName
} else {
    $packageRoot = (Get-Item -LiteralPath (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path).FullName
}

if (-not $EnvFile) {
    $EnvFile = Join-Path $packageRoot ".env"
} elseif (-not [System.IO.Path]::IsPathRooted($EnvFile)) {
    $EnvFile = Join-Path $packageRoot $EnvFile
}
if (-not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) {
    throw "Environment file not found: $EnvFile"
}
$EnvFile = (Get-Item -LiteralPath $EnvFile).FullName

if (-not $PythonExecutable) {
    $windowsVenvPython = Join-Path $packageRoot ".venv\Scripts\python.exe"
    $posixVenvPython = Join-Path $packageRoot ".venv\bin\python"
    if (Test-Path -LiteralPath $windowsVenvPython) {
        $PythonExecutable = $windowsVenvPython
    } elseif (Test-Path -LiteralPath $posixVenvPython) {
        $PythonExecutable = $posixVenvPython
    } else {
        $PythonExecutable = "python"
    }
}

$pythonScript = @'
from __future__ import annotations

import json
from pathlib import Path
import sys

from dotenv import dotenv_values
from dotenv.parser import parse_stream


env_path = Path(sys.argv[1])
with env_path.open(encoding="utf-8-sig") as stream:
    bindings = list(parse_stream(stream))

effective_values = dotenv_values(env_path, encoding="utf-8-sig")
seen: set[str] = set()
variables: list[dict[str, object]] = []
for binding in reversed(bindings):
    name = binding.key
    if not name or name in seen:
        continue
    seen.add(name)
    variables.append(
        {
            "Name": name,
            "Value": effective_values.get(name),
            "LineNumber": binding.original.line,
        }
    )

print(json.dumps(variables))
'@

$output = @($pythonScript | & $PythonExecutable - $EnvFile)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to parse environment file '$EnvFile'."
}
$variables = @($output -join [Environment]::NewLine | ConvertFrom-Json)

if ($IncludeValues) {
    $variables
} else {
    $variables | Select-Object -ExpandProperty Name
}