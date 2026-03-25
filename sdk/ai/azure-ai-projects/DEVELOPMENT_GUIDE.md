# Development Guide

## Emitting code from TypeSpec

For the time being, we have to emit using this dev version package: `"@azure-tools/typespec-client-generator-core": "0.67.0-dev.12"`,

The normal way to emit SDK using a dev package would be:
1. Go to `eng` folder in your azure-sdk-for-python clone.
1. Edit `emitter-package.json` to update the version of package `@azure-tools/typespec-client-generator-core`
1. Run `tsp-client generate-lock-file`. This should create the file `emitter-package-lock.json`.
1. Go to `sdk\ai\azure-ai-projects` and emit SDK as usual.

However, generating the lock file results in an error from a conflict resolving dependencies. That error should go away when the package is published as a major version instea of dev version.

The work around is the following:
1. In `sdk\ai\azure-ai-projects`, update the commit number in `tsp-location.yaml`
1. In that folder run `tsp-client sync`. This extracts the relevant TypeSpec souce code (for the particular commit) and copies it to the local folder `TempTypeSpecFiles`.
1. Cd to TempTypeSpecFiles folder
1. Copy `eng\emitter-package.json` as `package.json` in this folder
1. Edit `package.json` to update relevant package version
1. Run `npm install --legacy-peer-deps`. Then run `npm list` to make sure correct versions were installed.
1. Cd back up to folder `src\azure-sdk-for-python`, and run `tsp-client generate --save-inputs --skip-install`. This will emit code using already installed packages and the local TypeSpec files.

## Running post-processing

After emitting code from TypeSpec, you must run the script `post-emitter-fixes.cmd`

## Troubleshooting

Set this environment variable to get console logs of all network calls (AIProjectClient and OpenAI clients): `set AZURE_AI_PROJECTS_CONSOLE_LOGGING=true`





