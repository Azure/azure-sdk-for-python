# PowerShell script to convert LF to CRLF in .py files under _generated directories

# Define the base directory to search for files
$baseDirectory = "C:\repos\azure-sdk-for-python\sdk\search\azure-search-documents\azure\search\documents"

# Get all .py files recursively under _generated directories
$files = Get-ChildItem -Path $baseDirectory -Recurse -File -Filter "*.py" | Where-Object {
    $_.FullName -match "\\_generated\\"
}

foreach ($file in $files) {
    # Read the content of the file
    $content = Get-Content -Path $file.FullName -Raw

    # Replace LF with CRLF
    $content = $content -replace "(?<!\r)\n", "`r`n"

    # Write the updated content back to the file
    Set-Content -Path $file.FullName -Value $content -NoNewline

    Write-Host "Converted LF to CRLF in file: $($file.FullName)"
}

Write-Host "Conversion completed for all .py files under _generated directories."