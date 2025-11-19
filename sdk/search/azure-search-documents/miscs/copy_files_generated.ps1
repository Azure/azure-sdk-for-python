# PowerShell script to copy files from one directory to another

# Define source and destination directories
$source1 = "C:\repos\generated\knowledgebases\azure\search\documents\knowledgebases"
$destination1 = "C:\repos\azure-sdk-for-python\sdk\search\azure-search-documents\azure\search\documents\knowledgebases\_generated"

$source2 = "C:\repos\generated\searchindex\azure\search\documents"
$destination2 = "C:\repos\azure-sdk-for-python\sdk\search\azure-search-documents\azure\search\documents\_generated"

$source3 = "C:\repos\generated\searchservice\azure\search\documents\indexes"
$destination3 = "C:\repos\azure-sdk-for-python\sdk\search\azure-search-documents\azure\search\documents\indexes\_generated"

# Ensure the destination directories exist
if (-Not (Test-Path -Path $destination1)) {
    New-Item -ItemType Directory -Path $destination1 -Force
}
if (-Not (Test-Path -Path $destination2)) {
    New-Item -ItemType Directory -Path $destination2 -Force
}
if (-Not (Test-Path -Path $destination3)) {
    New-Item -ItemType Directory -Path $destination3 -Force
}

# Copy all files and subdirectories from sources to destinations
Copy-Item -Path "$source1\*" -Destination $destination1 -Recurse -Force
Copy-Item -Path "$source2\*" -Destination $destination2 -Recurse -Force
Copy-Item -Path "$source3\*" -Destination $destination3 -Recurse -Force

Write-Host "Files copied successfully from all sources to their respective destinations."