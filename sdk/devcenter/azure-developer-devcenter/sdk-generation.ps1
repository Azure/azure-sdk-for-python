Write-Host "TypeSpec Sync files"
ECHO 'y' | tsp-client sync

Write-Host "Update python client"
Move-item -Path 'TempTypeSpecFiles\DevCenter\python-client.tsp' -destination 'TempTypeSpecFiles\DevCenter\client.tsp' -Force

Write-Host "TypeSpec Generate"
ECHO 'y' | tsp-client generate