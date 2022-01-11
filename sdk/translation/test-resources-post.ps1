if ($DeploymentOutputs["TRANSLATION_DOCUMENT_STORAGE_NAME"] -ne "pythontranslationstorage") {
    $StorageAccount = Get-AzStorageAccount -ResourceGroupName $ResourceGroupName -Name $DeploymentOutputs["TRANSLATION_DOCUMENT_STORAGE_NAME"]
    $ctx = $StorageAccount.Context
    Set-AzStorageBlobContent -File "./sdk/translation/azure-ai-translation-document/samples/assets/glossary_sample.tsv" -Container "sourcecontainer" -Blob "glosario.tsv" -Context $ctx
    Set-AzStorageBlobContent -File "./sdk/translation/azure-ai-translation-document/samples/assets/translate.txt" -Container "sourcecontainer" -Blob "translate.txt" -Context $ctx
}
