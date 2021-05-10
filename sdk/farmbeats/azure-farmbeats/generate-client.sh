autorest --python \
    --input-file=swagger.json \
    --namespace=azure.farmbeats \
    --add-credential \
    --output-folder=azure \
    --title=FarmBeatsClient \
    --clear-output-folder \
    --credential-scope=https://farmbeats-dogfood.azure.net/.default \
    --package-version=1.0.0b1