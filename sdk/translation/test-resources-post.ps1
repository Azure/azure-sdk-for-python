[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param (
    [Parameter(Mandatory = $true)]
    [string] $ResourceGroupName,

    [Parameter()]
    [string] $TestApplicationOid,

    # The DeploymentOutputs parameter is only valid in the test-resources-post.ps1 script.
    [Parameter()]
    [hashtable] $DeploymentOutputs,

    # Captures any arguments from eng/New-TestResources.ps1 not declared here (no parameter errors).
    [Parameter(ValueFromRemainingArguments = $true)]
    $RemainingArguments
)

$StorageAccount = Get-AzStorageAccount -ResourceGroupName $ResourceGroupName -Name $DeploymentOutputs["TRANSLATION_DOCUMENT_STORAGE_NAME"]
$ctx = $StorageAccount.Context
Set-AzStorageBlobContent -File "./sdk/translation/azure-ai-translation-document/samples/assets/glossary_sample.tsv" -Container "sourcecontainer" -Blob "glosario.tsv" -Context $ctx
Set-AzStorageBlobContent -File "./sdk/translation/azure-ai-translation-document/samples/assets/translate.txt" -Container "sourcecontainer" -Blob "translate.txt" -Context $ctx
