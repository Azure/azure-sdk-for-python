# Using Azure Function HTTP Trigger

1. Add `azure-messaging-webpubsub-upstream` and `flask(recommend)` dependencies in `requirements.txt`.
1. Make sure that you have configured both `options` and `post` methods in your `function.json`, under `bindings` -> `methods`.