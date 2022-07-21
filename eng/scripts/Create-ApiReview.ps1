[CmdletBinding()]
Param (
  [Parameter(Mandatory=$True)]
  [array] $ArtifactList,
  [Parameter(Mandatory=$True)]
  [string] $ArtifactPath,
  [Parameter(Mandatory=$True)]
  [string] $APIViewUri,
  [Parameter(Mandatory=$True)]
  [string] $APIKey,
  [Parameter(Mandatory=$True)]
  [string] $SourceBranch,
  [Parameter(Mandatory=$True)]
  [string] $DefaultBranch,
  [Parameter(Mandatory=$True)]
  [string] $ConfigFileDir,
  [Parameter(Mandatory=$True)]
  [string] $buildId,
  [Parameter(Mandatory=$True)]
  [string] $repoName,
  [Parameter(Mandatory=$True)]
  [string] $Language
)

Set-StrictMode -Version 3
. (Join-Path $PSScriptRoot ".." common scripts common.ps1)

# Submit API review request and return status whether current revision is approved or pending or failed to create review
function Submit-APIReview($packageArtifactname, $apiLabel, $releaseStatus, $reviewFileName)
{
    $params = "buildId=$buildId&artifactName=packages&originalFilePath=$packageArtifactname&reviewFilePath=$reviewFileName"
    $params += "&label=$apiLabel&repoName=$repoName&packageName=$PackageName&project=internal"
    $uri = "$($APIViewUri)?$params"
    
    Write-Host $uri
    if ($releaseStatus -and ($releaseStatus -ne "Unreleased"))
    {
        $uri += "&compareAllRevisions=true"
    }

    $headers = @{
        "ApiKey" = $APIKey;
    }

    try
    {
        $Response = Invoke-WebRequest -Method 'GET' -Uri $uri -Headers $headers
        Write-Host "API Review URL: $($Response.Content)"
        $StatusCode = $Response.StatusCode
    }
    catch
    {
        Write-Host "Exception details: $($_.Exception)"
        $StatusCode = $_.Exception.Response.StatusCode
    }

    return $StatusCode
}

function ProcessPackage($PackageName)
{
    Write-Host "Artifact path: $($ArtifactPath)"
    Write-Host "Package Name: $($PackageName)"
    Write-Host "Source branch: $($SourceBranch)"
    Write-Host "Config File directory: $($ConfigFileDir)"

    $reviewFileName = "$($PackageName)_$($Language).json"

    $packages = @{}
    if ($FindArtifactForApiReviewFn -and (Test-Path "Function:$FindArtifactForApiReviewFn"))
    {
        $packages = &$FindArtifactForApiReviewFn $ArtifactPath $PackageName
    }
    else
    {
        Write-Host "The function for 'FindArtifactForApiReviewFn' was not found.`
        Make sure it is present in eng/scripts/Language-Settings.ps1 and referenced in eng/common/scripts/common.ps1.`
        See https://github.com/Azure/azure-sdk-tools/blob/main/doc/common/common_engsys.md#code-structure"
        return 1
    }

    if ($packages)
    {
        foreach($pkgPath in $packages.Values)
        {
            $pkg = Split-Path -Leaf $pkgPath
            $pkgPropPath = Join-Path -Path $ConfigFileDir "$PackageName.json"
            if (-Not (Test-Path $pkgPropPath))
            {
                Write-Host " Package property file path $($pkgPropPath) is invalid."
                continue
            }
            # Get package info from json file created before updating version to daily dev
            $pkgInfo = Get-Content $pkgPropPath | ConvertFrom-Json
            $version = [AzureEngSemanticVersion]::ParseVersionString($pkgInfo.Version)
            if ($version -eq $null)
            {
                Write-Host "Version info is not available for package $PackageName, because version '$(pkgInfo.Version)' is invalid. Please check if the version follows Azure SDK package versioning guidelines."
                return 1
            }

            Write-Host "Version: $($version)"
            Write-Host "SDK Type: $($pkgInfo.SdkType)"
            Write-Host "Release Status: $($pkgInfo.ReleaseStatus)"

            # Run create review step only if build is triggered from main branch or if version is GA.
            # This is to avoid invalidating review status by a build triggered from feature branch
            if ( ($SourceBranch -eq $DefaultBranch) -or (-not $version.IsPrerelease))
            {
                Write-Host "Submitting API Review for package $($pkg)"
                $respCode = Submit-APIReview -reviewFileName $reviewFileName -packageArtifactname $pkg -apiLabel $($pkgInfo.Version) -releaseStatus $pkgInfo.ReleaseStatus 
                Write-Host "HTTP Response code: $($respCode)"
                # HTTP status 200 means API is in approved status
                if ($respCode -eq '200')
                {
                    Write-Host "API review is in approved status."
                }
                elseif ($version.IsPrerelease)
                {
                    # Ignore API review status for prerelease version
                    Write-Host "Package version is not GA. Ignoring API view approval status"
                }
                elseif (!$pkgInfo.ReleaseStatus -or $pkgInfo.ReleaseStatus -eq "Unreleased")
                {
                    Write-Host "Release date is not set for current version in change log file for package. Ignoring API review approval status since package is not yet ready for release."
                }
                else
                {
                    # Return error code if status code is 201 for new data plane package
                    # Temporarily enable API review for spring SDK types. Ideally this should be done be using 'IsReviewRequired' method in language side
                    # to override default check of SDK type client
                    if (($pkgInfo.SdkType -eq "client" -or $pkgInfo.SdkType -eq "spring") -and $pkgInfo.IsNewSdk)
                    {
                        if ($respCode -eq '201')
                        {
                            Write-Host "Package version $($version) is GA and automatic API Review is not yet approved for package $($PackageName)."
                            Write-Host "Build and release is not allowed for GA package without API review approval."
                            Write-Host "You will need to queue another build to proceed further after API review is approved"
                            Write-Host "You can check http://aka.ms/azsdk/engsys/apireview/faq for more details on API Approval."
                        }
                        else 
                        {
                            Write-Host "Failed to create API Review for package $($PackageName). Please reach out to Azure SDK engineering systems on teams channel and share this build details."
                        }
                        return 1
                    }
                    else {
                        Write-Host "API review is not approved for package $($PackageName), however it is not required for this package type so it can still be released without API review approval."
                    }
                }
            }
            else {
                Write-Host "Build is triggered from $($SourceBranch) with prerelease version. Skipping API review status check."
            }
        }
    }
    else {
        Write-Host "No package is found in artifact path to submit review request"
    }
    return 0
}

$responses = @{}
# Check if package config file is present. This file has package version, SDK type etc info.
if (-not $ConfigFileDir)
{
    $ConfigFileDir = Join-Path -Path $ArtifactPath "PackageInfo"
}
foreach ($artifact in $ArtifactList)
{
    Write-Host "Processing $($artifact.name)"
    $result = ProcessPackage -PackageName $artifact.name
    $responses[$artifact.name] = $result 
}

$exitCode = 0
foreach($pkg in $responses.keys)
{    
    if ($responses[$pkg] -eq 1)
    {
        Write-Host "API changes are not approved for $($pkg)"
        $exitCode = 1
    }
}
exit $exitCode