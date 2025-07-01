<#
.SYNOPSIS
Azure SDK for Python - Complete TypeSpec Generation Workflow Script

.DESCRIPTION
This PowerShell script implements the complete TypeSpec SDK generation workflow 
for the azure-sdk-for-python repository as defined in generation.chatmode.md.

.PARAMETER ServiceName
The Azure service name (e.g., "eventgrid", "ai-projects")

.PARAMETER PackageName
The specific package name within the service

.PARAMETER TypeSpecPath
Path to local TypeSpec project or commit hash for remote TypeSpec

.PARAMETER WorkflowType
Type of workflow: "new", "update", "validation", "release"

.PARAMETER SkipValidation
Skip static validation steps

.PARAMETER AutoCommit
Automatically commit and push changes without confirmation

.EXAMPLE
.\Generate-AzureSDK.ps1 -ServiceName "eventgrid" -PackageName "azure-eventgrid" -WorkflowType "update"

.EXAMPLE
.\Generate-AzureSDK.ps1 -ServiceName "ai" -PackageName "azure-ai-projects" -TypeSpecPath "c:\local\typespec" -WorkflowType "new"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ServiceName,
    
    [Parameter(Mandatory = $false)]
    [string]$PackageName,
    
    [Parameter(Mandatory = $false)]
    [string]$TypeSpecPath,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("new", "update", "validation", "release", "custom")]
    [string]$WorkflowType = "update",
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipValidation,
    
    [Parameter(Mandatory = $false)]
    [switch]$AutoCommit,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force
)

# Script configuration
$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"
$VerbosePreference = "Continue"

# Global variables
$script:RepoRoot = $null
$script:ToxIniPath = $null
$script:PackagePath = $null
$script:CurrentBranch = $null
$script:StartTime = Get-Date

# Colors for output
$script:Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Phase = "Magenta"
    Command = "Blue"
}

#region Helper Functions

function Write-PhaseHeader {
    param([string]$Phase, [string]$Description)
    Write-Host "`n$('=' * 80)" -ForegroundColor $script:Colors.Phase
    Write-Host "PHASE $Phase: $Description" -ForegroundColor $script:Colors.Phase
    Write-Host "$('=' * 80)" -ForegroundColor $script:Colors.Phase
}

function Write-StepInfo {
    param([string]$Message)
    Write-Host "  ➤ $Message" -ForegroundColor $script:Colors.Info
}

function Write-CommandInfo {
    param([string]$Command, [string]$Purpose)
    Write-Host "`nCommand I'm about to run: " -NoNewline -ForegroundColor $script:Colors.Command
    Write-Host "`"$Command`"" -ForegroundColor White
    Write-Host "Purpose: $Purpose" -ForegroundColor $script:Colors.Info
}

function Test-Prerequisites {
    Write-StepInfo "Checking prerequisites..."
    
    # Check if we're in the azure-sdk-for-python repo
    $gitRemote = git remote get-url origin 2>$null
    if (-not $gitRemote -or $gitRemote -notmatch "azure-sdk-for-python") {
        throw "Not in azure-sdk-for-python repository. Please run from the repository root."
    }
    
    # Set repo root
    $script:RepoRoot = git rev-parse --show-toplevel 2>$null
    if (-not $script:RepoRoot) {
        $script:RepoRoot = (Get-Location).Path
    }
    
    # Set tox.ini path
    $script:ToxIniPath = Join-Path $script:RepoRoot "eng\tox\tox.ini"
    if (-not (Test-Path $script:ToxIniPath)) {
        throw "tox.ini not found at expected path: $script:ToxIniPath"
    }
    
    # Check required tools
    $requiredTools = @("python", "git", "gh", "tox")
    foreach ($tool in $requiredTools) {
        if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
            Write-Warning "$tool not found in PATH. Please install it."
        }
    }
    
    Write-Host "✓ Prerequisites validated" -ForegroundColor $script:Colors.Success
}

function Get-UserInput {
    param([string]$Prompt, [string[]]$ValidOptions = $null, [string]$Default = $null)
    
    do {
        if ($Default) {
            $input = Read-Host "$Prompt [$Default]"
            if ([string]::IsNullOrWhiteSpace($input)) {
                $input = $Default
            }
        } else {
            $input = Read-Host $Prompt
        }
        
        if ($ValidOptions -and $input -notin $ValidOptions) {
            Write-Host "Please choose from: $($ValidOptions -join ', ')" -ForegroundColor $script:Colors.Warning
            continue
        }
        
        return $input
    } while ($true)
}

function Invoke-SafeCommand {
    param(
        [string]$Command,
        [string]$Purpose,
        [switch]$IgnoreErrors,
        [switch]$NoOutput
    )
    
    Write-CommandInfo -Command $Command -Purpose $Purpose
    
    if (-not $Force) {
        $confirm = Get-UserInput "Execute this command? (y/n)" @("y", "n", "yes", "no") "y"
        if ($confirm -in @("n", "no")) {
            Write-Host "Skipped." -ForegroundColor $script:Colors.Warning
            return $null
        }
    }
    
    try {
        if ($NoOutput) {
            $result = Invoke-Expression $Command 2>$null
        } else {
            $result = Invoke-Expression $Command
        }
        
        if ($LASTEXITCODE -ne 0 -and -not $IgnoreErrors) {
            throw "Command failed with exit code $LASTEXITCODE"
        }
        
        return $result
    }
    catch {
        if ($IgnoreErrors) {
            Write-Warning "Command failed but continuing: $_"
            return $null
        } else {
            throw
        }
    }
}

function Test-PackageExists {
    param([string]$ServiceName, [string]$PackageName)
    
    $packagePath = Join-Path $script:RepoRoot "sdk\$ServiceName\$PackageName"
    return Test-Path $packagePath
}

function Get-PackageInfo {
    if (-not $ServiceName) {
        $ServiceName = Get-UserInput "Enter service name (e.g., eventgrid, ai)"
    }
    
    if (-not $PackageName) {
        $PackageName = Get-UserInput "Enter package name (e.g., azure-eventgrid)"
    }
    
    $script:PackagePath = Join-Path $script:RepoRoot "sdk\$ServiceName\$PackageName"
    
    return @{
        ServiceName = $ServiceName
        PackageName = $PackageName
        PackagePath = $script:PackagePath
        Exists = Test-Path $script:PackagePath
    }
}

#endregion

#region Phase Functions

function Phase1-ContextAssessment {
    Write-PhaseHeader "1" "CONTEXT ASSESSMENT & PREREQUISITES"
    
    Test-Prerequisites
    
    # Get current branch
    $script:CurrentBranch = git branch --show-current
    Write-StepInfo "Current branch: $script:CurrentBranch"
    
    if ($script:CurrentBranch -eq "main" -or $script:CurrentBranch -eq "master") {
        $createBranch = Get-UserInput "You're on main branch. Create feature branch? (y/n)" @("y", "n") "y"
        if ($createBranch -in @("y", "yes")) {
            $branchName = Get-UserInput "Enter branch name" $null "feature/sdk-generation-$(Get-Date -Format 'yyyyMMdd-HHmm')"
            Invoke-SafeCommand "git checkout -b $branchName" "Create and switch to feature branch"
            $script:CurrentBranch = $branchName
        }
    }
    
    # Context assessment questions
    Write-Host "`n🔍 CONTEXT ASSESSMENT" -ForegroundColor $script:Colors.Info
    Write-Host "I need to understand your scenario before proceeding." -ForegroundColor $script:Colors.Info
    
    if (-not $WorkflowType) {
        Write-Host "`nWhat specifically needs to be done?"
        Write-Host "1. TypeSpec changes/regeneration"
        Write-Host "2. Validation fixes only"  
        Write-Host "3. Version bump/release prep"
        Write-Host "4. New package creation"
        Write-Host "5. Custom workflow"
        
        $choice = Get-UserInput "Select option (1-5)" @("1", "2", "3", "4", "5")
        $WorkflowType = switch ($choice) {
            "1" { "update" }
            "2" { "validation" }
            "3" { "release" }
            "4" { "new" }
            "5" { "custom" }
        }
    }
    
    $packageInfo = Get-PackageInfo
    
    Write-Host "`n📋 WORKFLOW SUMMARY" -ForegroundColor $script:Colors.Success
    Write-Host "Service: $($packageInfo.ServiceName)" -ForegroundColor White
    Write-Host "Package: $($packageInfo.PackageName)" -ForegroundColor White
    Write-Host "Workflow: $WorkflowType" -ForegroundColor White
    Write-Host "Package exists: $($packageInfo.Exists)" -ForegroundColor White
    Write-Host "Branch: $script:CurrentBranch" -ForegroundColor White
    
    return $packageInfo
}

function Phase2-EnvironmentVerification {
    param($PackageInfo)
    
    Write-PhaseHeader "2" "ENVIRONMENT VERIFICATION"
    
    Write-StepInfo "Checking Python virtual environment..."
    $pythonPath = (Get-Command python).Source
    $isVenv = $env:VIRTUAL_ENV -or ($pythonPath -match "venv|env")
    
    if (-not $isVenv) {
        Write-Warning "No virtual environment detected. Consider activating one."
        $createVenv = Get-UserInput "Create and activate virtual environment? (y/n)" @("y", "n") "y"
        
        if ($createVenv -in @("y", "yes")) {
            $venvPath = Join-Path $script:RepoRoot ".venv"
            Invoke-SafeCommand "python -m venv $venvPath" "Create virtual environment"
            Invoke-SafeCommand "$venvPath\Scripts\Activate.ps1" "Activate virtual environment"
        }
    } else {
        Write-Host "✓ Virtual environment active: $env:VIRTUAL_ENV" -ForegroundColor $script:Colors.Success
    }
    
    Write-StepInfo "Installing/updating required packages..."
    $toolsPath = Join-Path $script:RepoRoot "tools\azure-sdk-tools"
    if (Test-Path $toolsPath) {
        Invoke-SafeCommand "pip install -e `"$toolsPath`"" "Install azure-sdk-tools"
    }
    
    # Check for dev_requirements.txt
    $devReqPath = Join-Path $script:RepoRoot "dev_requirements.txt"
    if (Test-Path $devReqPath) {
        Invoke-SafeCommand "pip install -r `"$devReqPath`"" "Install development requirements"
    }
    
    Write-Host "✓ Environment verification complete" -ForegroundColor $script:Colors.Success
}

function Phase3-SDKGeneration {
    param($PackageInfo, $WorkflowType)
    
    Write-PhaseHeader "3" "SDK GENERATION"
    Write-Host "⏱️ TIME EXPECTATION: 5-6 minutes" -ForegroundColor $script:Colors.Info
    
    if ($WorkflowType -eq "validation") {
        Write-StepInfo "Skipping SDK generation for validation-only workflow"
        return
    }
    
    Set-Location $script:RepoRoot
    
    switch ($WorkflowType) {
        "new" {
            Write-StepInfo "Generating new SDK package..."
            
            if (-not $TypeSpecPath) {
                $TypeSpecPath = Get-UserInput "Enter TypeSpec location (local path or commit hash)"
            }
            
            $isLocal = Test-Path $TypeSpecPath
            if ($isLocal) {
                $command = "python scripts/quickstart_tooling_dpg/init_local.py --local-typespec-dir `"$TypeSpecPath`""
            } else {
                $command = "python scripts/quickstart_tooling_dpg/init.py --package-name $($PackageInfo.PackageName) --commit-hash $TypeSpecPath"
            }
            
            Invoke-SafeCommand $command "Initialize new SDK package"
        }
        
        "update" {
            Write-StepInfo "Updating existing SDK package..."
            
            if (-not $PackageInfo.Exists) {
                throw "Package does not exist. Use 'new' workflow type instead."
            }
            
            if (-not $TypeSpecPath) {
                $useExisting = Get-UserInput "Use existing TypeSpec configuration? (y/n)" @("y", "n") "y"
                if ($useExisting -eq "n") {
                    $TypeSpecPath = Get-UserInput "Enter new TypeSpec commit hash"
                }
            }
            
            $command = if ($TypeSpecPath) {
                "python scripts/quickstart_tooling_dpg/update.py --package-path `"$($PackageInfo.PackagePath)`" --commit-hash $TypeSpecPath"
            } else {
                "python scripts/quickstart_tooling_dpg/update.py --package-path `"$($PackageInfo.PackagePath)`""
            }
            
            Invoke-SafeCommand $command "Update SDK package"
        }
        
        "release" {
            Write-StepInfo "Preparing package for release..."
            # Version bump and changelog updates would go here
            Write-Warning "Release preparation requires manual version and changelog updates"
        }
        
        "custom" {
            Write-StepInfo "Custom workflow - manual intervention required"
            $customCommand = Get-UserInput "Enter custom generation command (or press Enter to skip)"
            if ($customCommand) {
                Invoke-SafeCommand $customCommand "Execute custom command"
            }
        }
    }
    
    Write-Host "✓ SDK generation complete" -ForegroundColor $script:Colors.Success
}

function Phase4-IterativeFlowSelection {
    Write-PhaseHeader "4" "ITERATIVE FLOW SELECTION"
    
    $flows = @{
        "1" = @{ Name = "TypeSpec Client Customization (client.tsp)"; Description = "TypeSpec-level customizations" }
        "2" = @{ Name = "Python Patch File Approach (_patch.py)"; Description = "Python-specific modifications" }
        "4" = @{ Name = "Generate & Record Tests"; Description = "Test infrastructure setup" }
        "5" = @{ Name = "Update & Re-record Tests"; Description = "Refresh tests after updates" }
        "6" = @{ Name = "Update & Test Samples"; Description = "Sample validation and updates" }
        "7" = @{ Name = "Documentation & Release Preparation"; Description = "Release documentation" }
        "skip" = @{ Name = "Skip to Validation"; Description = "Proceed to static validation" }
    }
    
    do {
        Write-Host "`n📋 AVAILABLE FLOWS:" -ForegroundColor $script:Colors.Info
        foreach ($key in $flows.Keys | Sort-Object) {
            Write-Host "  $key. $($flows[$key].Name)" -ForegroundColor White
            Write-Host "     $($flows[$key].Description)" -ForegroundColor Gray
        }
        
        $selection = Get-UserInput "Select flow (1,2,4,5,6,7) or 'skip' to continue" ($flows.Keys)
        
        if ($selection -eq "skip") {
            break
        }
        
        switch ($selection) {
            "1" { Invoke-Flow1-TypeSpecCustomization }
            "2" { Invoke-Flow2-PythonPatch }
            "4" { Invoke-Flow4-GenerateTests }
            "5" { Invoke-Flow5-UpdateTests }
            "6" { Invoke-Flow6-UpdateSamples }
            "7" { Invoke-Flow7-Documentation }
        }
        
        $continue = Get-UserInput "Select another flow? (y/n)" @("y", "n") "n"
    } while ($continue -in @("y", "yes"))
}

function Invoke-Flow1-TypeSpecCustomization {
    Write-Host "`n🔧 FLOW 1: TypeSpec Client Customization" -ForegroundColor $script:Colors.Phase
    
    $clientTspPath = Join-Path $script:PackagePath "client.tsp"
    
    if (Test-Path $clientTspPath) {
        Write-Host "Found existing client.tsp file" -ForegroundColor $script:Colors.Success
        $edit = Get-UserInput "Edit client.tsp file? (y/n)" @("y", "n") "y"
        if ($edit -in @("y", "yes")) {
            Start-Process "code" -ArgumentList "`"$clientTspPath`""
            Read-Host "Press Enter when editing is complete"
        }
    } else {
        Write-Host "No client.tsp file found. Create one?" -ForegroundColor $script:Colors.Warning
        $create = Get-UserInput "Create client.tsp? (y/n)" @("y", "n") "n"
        if ($create -in @("y", "yes")) {
            # Create basic client.tsp template
            $template = @"
import "@azure-tools/typespec-client-generator-core";
import "./main.tsp";

using Azure.ClientGenerator.Core;

// Add your TypeSpec customizations here
"@
            Set-Content -Path $clientTspPath -Value $template
            Start-Process "code" -ArgumentList "`"$clientTspPath`""
            Read-Host "Press Enter when editing is complete"
        }
    }
    
    # Regenerate after TypeSpec changes
    $regenerate = Get-UserInput "Regenerate SDK after TypeSpec changes? (y/n)" @("y", "n") "y"
    if ($regenerate -in @("y", "yes")) {
        Invoke-SafeCommand "python scripts/quickstart_tooling_dpg/update.py --package-path `"$script:PackagePath`"" "Regenerate SDK with TypeSpec changes"
    }
}

function Invoke-Flow2-PythonPatch {
    Write-Host "`n🔧 FLOW 2: Python Patch File Approach" -ForegroundColor $script:Colors.Phase
    
    # Find _patch.py files
    $patchFiles = Get-ChildItem -Path $script:PackagePath -Name "*_patch.py" -Recurse
    
    if ($patchFiles) {
        Write-Host "Found patch files:" -ForegroundColor $script:Colors.Success
        $patchFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
        
        $edit = Get-UserInput "Edit patch files? (y/n)" @("y", "n") "y"
        if ($edit -in @("y", "yes")) {
            foreach ($file in $patchFiles) {
                $fullPath = Join-Path $script:PackagePath $file
                Start-Process "code" -ArgumentList "`"$fullPath`""
            }
            Read-Host "Press Enter when editing is complete"
        }
    } else {
        Write-Host "No _patch.py files found." -ForegroundColor $script:Colors.Warning
        Write-Host "Patch files are automatically created during generation if needed." -ForegroundColor $script:Colors.Info
    }
}

function Invoke-Flow4-GenerateTests {
    Write-Host "`n🔧 FLOW 4: Generate & Record Tests" -ForegroundColor $script:Colors.Phase
    
    $testsPath = Join-Path $script:PackagePath "tests"
    
    if (-not (Test-Path $testsPath)) {
        Write-StepInfo "Creating tests directory structure..."
        New-Item -Path $testsPath -ItemType Directory -Force | Out-Null
    }
    
    # Generate test templates
    $generateTests = Get-UserInput "Generate test templates? (y/n)" @("y", "n") "y"
    if ($generateTests -in @("y", "yes")) {
        $command = "python scripts/quickstart_tooling_dpg/generate_tests.py --package-path `"$script:PackagePath`""
        Invoke-SafeCommand $command "Generate test templates" -IgnoreErrors
    }
    
    # Bicep infrastructure
    $generateBicep = Get-UserInput "Generate Bicep infrastructure files? (y/n)" @("y", "n") "y"
    if ($generateBicep -in @("y", "yes")) {
        $bicepPath = Join-Path $testsPath "bicep"
        if (-not (Test-Path $bicepPath)) {
            New-Item -Path $bicepPath -ItemType Directory -Force | Out-Null
        }
        Write-Host "Bicep template creation requires manual setup based on service requirements" -ForegroundColor $script:Colors.Warning
    }
}

function Invoke-Flow5-UpdateTests {
    Write-Host "`n🔧 FLOW 5: Update & Re-record Tests" -ForegroundColor $script:Colors.Phase
    
    $testsPath = Join-Path $script:PackagePath "tests"
    
    if (-not (Test-Path $testsPath)) {
        Write-Warning "No tests directory found"
        return
    }
    
    # Re-record tests
    $rerecord = Get-UserInput "Re-record test recordings? (y/n)" @("y", "n") "y"
    if ($rerecord -in @("y", "yes")) {
        Set-Location $script:PackagePath
        $command = "python -m pytest tests/ --record-mode=rewrite"
        Invoke-SafeCommand $command "Re-record test recordings" -IgnoreErrors
        Set-Location $script:RepoRoot
    }
}

function Invoke-Flow6-UpdateSamples {
    Write-Host "`n🔧 FLOW 6: Update & Test Samples" -ForegroundColor $script:Colors.Phase
    
    $samplesPath = Join-Path $script:PackagePath "samples"
    
    if (-not (Test-Path $samplesPath)) {
        Write-StepInfo "Creating samples directory..."
        New-Item -Path $samplesPath -ItemType Directory -Force | Out-Null
    }
    
    # Generate sample templates
    $generateSamples = Get-UserInput "Generate sample templates? (y/n)" @("y", "n") "y"
    if ($generateSamples -in @("y", "yes")) {
        $command = "python scripts/quickstart_tooling_dpg/generate_samples.py --package-path `"$script:PackagePath`""
        Invoke-SafeCommand $command "Generate sample templates" -IgnoreErrors
    }
    
    # Test samples
    $testSamples = Get-UserInput "Test samples? (y/n)" @("y", "n") "n"
    if ($testSamples -in @("y", "yes")) {
        Set-Location $script:PackagePath
        $command = "tox -e samples -c `"$script:ToxIniPath`" --root ."
        Invoke-SafeCommand $command "Test samples" -IgnoreErrors
        Set-Location $script:RepoRoot
    }
}

function Invoke-Flow7-Documentation {
    Write-Host "`n🔧 FLOW 7: Documentation & Release Preparation" -ForegroundColor $script:Colors.Phase
    
    # Update CHANGELOG.md
    $changelogPath = Join-Path $script:PackagePath "CHANGELOG.md"
    if (Test-Path $changelogPath) {
        $editChangelog = Get-UserInput "Edit CHANGELOG.md? (y/n)" @("y", "n") "y"
        if ($editChangelog -in @("y", "yes")) {
            Start-Process "code" -ArgumentList "`"$changelogPath`""
            Read-Host "Press Enter when editing is complete"
        }
    }
    
    # Update README.md
    $readmePath = Join-Path $script:PackagePath "README.md"
    if (Test-Path $readmePath) {
        $editReadme = Get-UserInput "Edit README.md? (y/n)" @("y", "n") "n"
        if ($editReadme -in @("y", "yes")) {
            Start-Process "code" -ArgumentList "`"$readmePath`""
            Read-Host "Press Enter when editing is complete"
        }
    }
    
    # Version update
    $updateVersion = Get-UserInput "Update version? (y/n)" @("y", "n") "n"
    if ($updateVersion -in @("y", "yes")) {
        $newVersion = Get-UserInput "Enter new version (e.g., 1.0.0)"
        $versionFile = Join-Path $script:PackagePath "azure" "*" "*" "_version.py"
        $versionFiles = Get-ChildItem -Path $versionFile -ErrorAction SilentlyContinue
        
        foreach ($file in $versionFiles) {
            Write-Host "Update version in: $($file.FullName)" -ForegroundColor $script:Colors.Info
            # Manual version update would be required here
        }
    }
}

function Phase5-StaticValidation {
    param($PackageInfo)
    
    if ($SkipValidation) {
        Write-Host "Skipping validation (SkipValidation flag set)" -ForegroundColor $script:Colors.Warning
        return
    }
    
    Write-PhaseHeader "5" "STATIC VALIDATION (SEQUENTIAL)"
    Write-Host "⏱️ TIME EXPECTATION: 3-5 minutes per validation step" -ForegroundColor $script:Colors.Info
    
    Set-Location $PackageInfo.PackagePath
    
    $validationSteps = @(
        @{ Name = "pylint"; Command = "tox -e pylint -c `"$script:ToxIniPath`" --root ."; Required = $true }
        @{ Name = "mypy"; Command = "tox -e mypy -c `"$script:ToxIniPath`" --root ."; Required = $true }
        @{ Name = "pyright"; Command = "tox -e pyright -c `"$script:ToxIniPath`" --root ."; Required = $false }
        @{ Name = "verifytypes"; Command = "tox -e verifytypes -c `"$script:ToxIniPath`" --root ."; Required = $false }
        @{ Name = "sphinx"; Command = "tox -e sphinx -c `"$script:ToxIniPath`" --root ."; Required = $true }
        @{ Name = "mindependency"; Command = "tox -e mindependency -c `"$script:ToxIniPath`" --root ."; Required = $false }
        @{ Name = "bandit"; Command = "tox -e bandit -c `"$script:ToxIniPath`" --root ."; Required = $false }
        @{ Name = "black"; Command = "tox -e black -c `"$script:ToxIniPath`" --root ."; Required = $false }
        @{ Name = "samples"; Command = "tox -e samples -c `"$script:ToxIniPath`" --root ."; Required = $false }
        @{ Name = "breaking"; Command = "tox -e breaking -c `"$script:ToxIniPath`" --root ."; Required = $false }
    )
    
    $results = @{}
    
    foreach ($step in $validationSteps) {
        Write-Host "`n🔍 Running $($step.Name) validation..." -ForegroundColor $script:Colors.Info
        
        $runStep = Get-UserInput "Run $($step.Name)? (y/n/s for skip all)" @("y", "n", "s") "y"
        
        if ($runStep -eq "s") {
            Write-Host "Skipping remaining validation steps" -ForegroundColor $script:Colors.Warning
            break
        }
        
        if ($runStep -eq "n") {
            $results[$step.Name] = "SKIPPED"
            continue
        }
        
        try {
            Invoke-SafeCommand $step.Command "Run $($step.Name) validation" -IgnoreErrors
            $results[$step.Name] = if ($LASTEXITCODE -eq 0) { "PASS" } else { "FAIL" }
            
            if ($results[$step.Name] -eq "FAIL" -and $step.Required) {
                Write-Warning "$($step.Name) failed - this is a release blocking check"
                $fix = Get-UserInput "Attempt to fix issues? (y/n)" @("y", "n") "n"
                if ($fix -eq "y") {
                    Write-Host "Please fix issues manually and re-run validation" -ForegroundColor $script:Colors.Warning
                    Read-Host "Press Enter when fixes are complete"
                    
                    # Re-run the step
                    Invoke-SafeCommand $step.Command "Re-run $($step.Name) validation" -IgnoreErrors
                    $results[$step.Name] = if ($LASTEXITCODE -eq 0) { "PASS" } else { "FAIL" }
                }
            }
        }
        catch {
            $results[$step.Name] = "ERROR"
            Write-Warning "$($step.Name) encountered an error: $_"
        }
    }
    
    # Validation summary
    Write-Host "`n📊 VALIDATION SUMMARY" -ForegroundColor $script:Colors.Phase
    $releaseBlocking = @()
    
    foreach ($step in $validationSteps) {
        $result = $results[$step.Name]
        if (-not $result) { $result = "NOT_RUN" }
        
        $color = switch ($result) {
            "PASS" { $script:Colors.Success }
            "FAIL" { $script:Colors.Error }
            "ERROR" { $script:Colors.Error }
            default { $script:Colors.Warning }
        }
        
        Write-Host "  $($step.Name): $result" -ForegroundColor $color
        
        if ($step.Required -and $result -in @("FAIL", "ERROR")) {
            $releaseBlocking += $step.Name
        }
    }
    
    if ($releaseBlocking) {
        Write-Host "`n⚠️ RELEASE BLOCKING ISSUES:" -ForegroundColor $script:Colors.Error
        $releaseBlocking | ForEach-Object { Write-Host "  - $_" -ForegroundColor $script:Colors.Error }
    } else {
        Write-Host "✓ All required validations passed" -ForegroundColor $script:Colors.Success
    }
    
    Set-Location $script:RepoRoot
}

function Phase6-CommitAndPush {
    Write-PhaseHeader "6" "COMMIT AND PUSH"
    
    # Show changed files
    $changedFiles = git diff --name-only
    $stagedFiles = git diff --staged --name-only
    
    if ($changedFiles -or $stagedFiles) {
        Write-Host "`n📁 CHANGED FILES:" -ForegroundColor $script:Colors.Info
        
        if ($changedFiles) {
            Write-Host "Unstaged changes:" -ForegroundColor $script:Colors.Warning
            $changedFiles | Where-Object { $_ -notmatch "^\.github|^\.vscode" } | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
        }
        
        if ($stagedFiles) {
            Write-Host "Staged changes:" -ForegroundColor $script:Colors.Success
            $stagedFiles | Where-Object { $_ -notmatch "^\.github|^\.vscode" } | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
        }
        
        if (-not $AutoCommit) {
            $commit = Get-UserInput "Commit and push changes? (y/n)" @("y", "n") "y"
        } else {
            $commit = "y"
        }
        
        if ($commit -in @("y", "yes")) {
            # Stage all changes
            if ($changedFiles) {
                Invoke-SafeCommand "git add ." "Stage all changes"
            }
            
            # Commit
            $defaultMessage = "feat: SDK generation for $($PackageInfo.ServiceName)/$($PackageInfo.PackageName)"
            $commitMessage = Get-UserInput "Enter commit message" $null $defaultMessage
            
            Invoke-SafeCommand "git commit -m `"$commitMessage`"" "Commit changes"
            
            # Push
            $push = Get-UserInput "Push to remote? (y/n)" @("y", "n") "y"
            if ($push -in @("y", "yes")) {
                Invoke-SafeCommand "git push origin $script:CurrentBranch" "Push changes to remote"
            }
        }
    } else {
        Write-Host "No changes to commit" -ForegroundColor $script:Colors.Info
    }
}

function Phase7-PullRequestManagement {
    Write-PhaseHeader "7" "PULL REQUEST MANAGEMENT"
    
    # Check if gh CLI is authenticated
    $ghAuth = gh auth status 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "GitHub CLI not authenticated"
        $auth = Get-UserInput "Authenticate with GitHub CLI? (y/n)" @("y", "n") "y"
        if ($auth -in @("y", "yes")) {
            Invoke-SafeCommand "gh auth login" "Authenticate with GitHub CLI"
        } else {
            Write-Warning "Skipping pull request management"
            return
        }
    }
    
    # Check for existing PR
    $existingPR = gh pr view --json number,title,state 2>$null | ConvertFrom-Json -ErrorAction SilentlyContinue
    
    if ($existingPR) {
        Write-Host "Existing PR found:" -ForegroundColor $script:Colors.Success
        Write-Host "  #$($existingPR.number): $($existingPR.title)" -ForegroundColor White
        Write-Host "  State: $($existingPR.state)" -ForegroundColor White
        
        $updatePR = Get-UserInput "Update existing PR? (y/n)" @("y", "n") "y"
        if ($updatePR -in @("y", "yes")) {
            # PR is updated automatically by push
            Write-Host "PR updated with latest changes" -ForegroundColor $script:Colors.Success
        }
    } else {
        # Create new PR
        $createPR = Get-UserInput "Create new pull request? (y/n)" @("y", "n") "y"
        if ($createPR -in @("y", "yes")) {
            $prTitle = Get-UserInput "Enter PR title" $null "SDK generation for $($PackageInfo.ServiceName)/$($PackageInfo.PackageName)"
            $prBody = Get-UserInput "Enter PR description" $null "Automated SDK generation and validation"
            
            $command = "gh pr create --title `"$prTitle`" --body `"$prBody`" --draft"
            Invoke-SafeCommand $command "Create draft pull request"
            
            # Get PR info
            $newPR = gh pr view --json number,url | ConvertFrom-Json
            Write-Host "✓ Created PR #$($newPR.number): $($newPR.url)" -ForegroundColor $script:Colors.Success
        }
    }
}

function Phase8-ReleaseReadiness {
    param($PackageInfo)
    
    Write-PhaseHeader "8" "RELEASE READINESS & HANDOFF"
    
    # Package readiness check would require azure-sdk-python-mcp tool
    Write-StepInfo "Checking package readiness status..."
    Write-Host "Note: Package readiness check requires azure-sdk-python-mcp integration" -ForegroundColor $script:Colors.Warning
    
    # PR URL
    $prInfo = gh pr view --json number,url 2>$null | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($prInfo) {
        Write-Host "`n🔗 PULL REQUEST:" -ForegroundColor $script:Colors.Success
        Write-Host "  $($prInfo.url)" -ForegroundColor White
    }
    
    # Next steps
    Write-Host "`n📋 NEXT STEPS:" -ForegroundColor $script:Colors.Info
    Write-Host "  1. Review PR checks and validation results" -ForegroundColor White
    Write-Host "  2. Address any failing checks" -ForegroundColor White
    Write-Host "  3. Request review from SDK architects" -ForegroundColor White
    Write-Host "  4. Use azure-rest-api-specs agent for TypeSpec updates if needed" -ForegroundColor White
    
    # Completion summary
    $endTime = Get-Date
    $duration = $endTime - $script:StartTime
    
    Write-Host "`n🎉 WORKFLOW COMPLETE!" -ForegroundColor $script:Colors.Success
    Write-Host "Total execution time: $($duration.ToString('mm\:ss'))" -ForegroundColor $script:Colors.Success
}

#endregion

#region Main Execution

function Main {
    try {
        Write-Host "🚀 Azure SDK for Python - TypeSpec Generation Workflow" -ForegroundColor $script:Colors.Phase
        Write-Host "Starting workflow execution..." -ForegroundColor $script:Colors.Info
        
        # Phase 1: Context Assessment
        $packageInfo = Phase1-ContextAssessment
        
        # Phase 2: Environment Verification
        Phase2-EnvironmentVerification -PackageInfo $packageInfo
        
        # Phase 3: SDK Generation
        Phase3-SDKGeneration -PackageInfo $packageInfo -WorkflowType $WorkflowType
        
        # Phase 4: Iterative Flow Selection
        Phase4-IterativeFlowSelection
        
        # Phase 5: Static Validation
        Phase5-StaticValidation -PackageInfo $packageInfo
        
        # Phase 6: Commit and Push
        Phase6-CommitAndPush
        
        # Phase 7: Pull Request Management
        Phase7-PullRequestManagement
        
        # Phase 8: Release Readiness
        Phase8-ReleaseReadiness -PackageInfo $packageInfo
        
    }
    catch {
        Write-Host "`n❌ ERROR: $_" -ForegroundColor $script:Colors.Error
        Write-Host "Stack trace:" -ForegroundColor $script:Colors.Error
        Write-Host $_.ScriptStackTrace -ForegroundColor Gray
        exit 1
    }
}

# Script entry point
if ($MyInvocation.InvocationName -ne ".") {
    Main
}

#endregion
