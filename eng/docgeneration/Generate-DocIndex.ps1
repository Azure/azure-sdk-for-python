[CmdletBinding()]
Param (
    $RepoRoot,
    $DocGenDir,
    $ExcludeDocIndexFile = "$PSScriptRoot/exclude-doc-index.json",
    $lang = "python"
)

# Import required scripts
. (Join-Path $PSScriptRoot ../common/scripts/common.ps1)

# There are some artifact that show up, due to the way we do discovery, that are never shipped.
# Keep a list of those here and anything we don't want to ship can be added to here which will
# cause them to get skipped when generating the DocIndex
$ExcludeData = Get-Content -Raw -Path $ExcludeDocIndexFile | ConvertFrom-Json

Write-Verbose "Name Reccuring paths with variable names"
$DocFxTool = "${RepoRoot}/docfx/docfx.exe"
$DocOutDir = "${RepoRoot}/docfx_project"

Write-Verbose "Initializing Default DocFx Site..."
& "${DocFxTool}" init -q -o "${DocOutDir}"

Write-Verbose "Copying template and configuration..."
New-Item -Path "${DocOutDir}" -Name "templates" -ItemType "directory" -Force
Copy-Item "${DocGenDir}/templates/*" -Destination "${DocOutDir}/templates" -Force -Recurse
Copy-Item "${DocGenDir}/docfx.json" -Destination "${DocOutDir}/" -Force

Write-Verbose "Creating Index using service directory and package names from repo..."

# The list of services is being constructed from the directory list under the sdk folder
# which, right now, only contains client/data directories. When management is moved to
# the under sdk it'll automatically get picked up.
$ServiceListData = Get-ChildItem "${RepoRoot}/sdk" -Directory | Where-Object {$_.PSIsContainer}
$YmlPath = "${DocOutDir}/api"
New-Item -Path $YmlPath -Name "toc.yml" -Force

$metadata = GetMetaData -lang $lang
foreach ($serviceDir in $ServiceListData)
{   
    $dirName = $serviceDir.name
    if ($ExcludeData -and ($ExcludeData.services -contains $dirName)) {
        continue
    }
    $serviceName = ""
    # Store the list of artifacts into the arrays and write them into the .md file
    # after processing the list of subdirectories. This will allow the correct 
    # division of the artifacts under the Client or Management headings
    $clientArr = @()
    $artifacts = Get-AllPkgProperties -ServiceDirectory $dirName
    foreach ($pkgInfo in $artifacts) {
        if (!$serviceName) {
            $serviceInfo = $metadata | ? { $_.Package -eq $pkgInfo.Name -and $_.GroupId -eq $pkgInfo.Group} 
            if ($serviceInfo -and $serviceInfo.ServiceName) {
                $serviceName = $serviceInfo.ServiceName
            } 
            else {
                $serviceName = (Get-Culture).TextInfo.ToTitleCase($dirName.ToLower())
            }
        }
        if ($ExcludeData -and ($ExcludeData.artifacts -contains $pkgInfo.Name)) {
            continue
        }
        $clientArr += $pkgInfo.Name
    }
  
    # Only create this if there's something to create
    #if (($clientArr.Count -gt 0) -or ($mgmtArr.Count -gt 0))
    if ($clientArr.Count -gt 0)
    {
        New-Item -Path $YmlPath -Name "${dirName}.md" -Force
        Add-Content -Path "$($YmlPath)/toc.yml" -Value "- name: ${serviceName}`r`n  href: ${dirName}.md"
        # loop through the arrays and add the appropriate artifacts under the appropriate headings
        if ($clientArr.Count -gt 0)
        {
            Add-Content -Path "$($YmlPath)/${dirName}.md" -Value "# Client Libraries"
            foreach($lib in $clientArr) 
            {
                Write-Host "Write $($lib) to ${dirName}.md"
                Add-Content -Path "$($YmlPath)/${dirName}.md" -Value "#### $lib"
            }
        }
        # For the moment there are no management docs and with the way some of the libraries
        # in management are versioned is a bit wonky. They aren't versioned by releasing a new
        # version with the same groupId/artifactId, they're versioned with the same artifactId
        # and version with a different groupId and the groupId happens to include the date. For 
        # example, the artifact/version of azure-mgmt-storage:1.0.0-beta has several different 
        # groupIds. com.microsoft.azure.storage.v2016_01_01, com.microsoft.azure.storage.v2017_10_01,
        # com.microsoft.azure.storage.v2018_11_01 etc.
        #if ($mgmtArr.Count -gt 0) 
        #{
        #    Add-Content -Path "$($YmlPath)/$($Dir.Name).md" -Value "# Management Libraries"
        #    foreach($lib in $mgmtArr) 
        #    {
        #        Write-Output "Write $($lib) to $($Dir.Name).md"
        #        Add-Content -Path "$($YmlPath)/$($Dir.Name).md" -Value "#### $lib"
        #    }
        #}
    }
}

Write-Verbose "Creating Site Title and Navigation..."
New-Item -Path "${DocOutDir}" -Name "toc.yml" -Force
Add-Content -Path "${DocOutDir}/toc.yml" -Value "- name: Azure SDK for Python APIs`r`n  href: api/`r`n  homepage: api/index.md"

Write-Verbose "Copying root markdowns"
Copy-Item "$($RepoRoot)/README.md" -Destination "${DocOutDir}/api/index.md" -Force

Write-Verbose "Building site..."
& "${DocFxTool}" build "${DocOutDir}/docfx.json"

Copy-Item "${DocGenDir}/assets/logo.svg" -Destination "${DocOutDir}/_site/" -Force