<#
```
Invoke-Pester -Output Detailed $PSScriptRoot/Validation.Tests.ps1
We are testing the ValidatePackagesForDocs function in Language-Settings.sp1
```
#>
Import-Module Pester
BeforeDiscovery {
  $RexToolSpecs = Get-Content "$PSScriptRoot/rex-tool-tests.json" | ConvertFrom-Json -AsHashtable
}

BeforeAll {
  . $PSScriptRoot/../../../common/scripts/common.ps1

  python3.11 -m venv $PSScriptRoot/.env
  # TODO: This may be OS-Specific (Linux: .env/bin, Windows: .env/Scripts)
  . $PSScriptRoot/.env/bin/Activate.ps1
  
  if (!(Get-Command py2docfx -ErrorAction SilentlyContinue)) { 
    # TODO: Pin this to a specific version
    pip install py2docfx
  }
}

AfterAll {
    # Clean up Python venv
    deactivate 
    Remove-Item $PSScriptRoot/.env -Recurse -Force -ErrorAction SilentlyContinue
}

function GetPackageSpecs() {
  Get-Content "$PSScriptRoot/rex-tool-tests.json" | ConvertFrom-Json
}

# Test plan:
# 1. Tests on a list of packages which some of the packages pass the validation and the rest fail the validation.
Describe "ValidatePackagesForDocs" -Tag "UnitTest" {
  It "Package <Package> returns result <ExpectedResult>" -ForEach $RexToolSpecs {
    # $output = ValidatePackagesForDocs -packages @{ name = $Package }
    # $output.Success | Should -Be $ExpectedResult
    python -m py2docfx `
        --install-type pypi `
        --package-name $Package `
        --version $Version `
        --prefer-source-distribution | Out-Null

    $result = $LASTEXITCODE -eq 0
    $result | Should -Be $ExpectedResult
  }
}