# resolve-error

Test how resolve errors are handled when a tag points to an input-file that does
not contian valid JSON.

```yaml
openapi-type: arm
openapi-subtype: rpaas
tag: package-2021-11-01
```

### Tag: package-2021-11-01

These settings apply only when `--tag=package-2021-11-01` is specified on the command line.

```yaml $(tag) == 'package-2021-11-01'
input-file:
  - invalid-json.json
```
