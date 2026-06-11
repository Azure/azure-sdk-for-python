# Test date parsing in YAML decoding

> see https://aka.ms/autorest

This is the AutoRest configuration file for Contoso.WidgetManager.

## Configuration

### Basic Information

Use a date-only string (leading or following qualifiers like "package", "preview", etc.). The YAML parser should
parse this as a string and not a Date.

```yaml
openapi-type: data-plane
tag: 2022-12-01
```

### Tag: 2022-12-01

These settings apply only when `--tag=package-2022-12-01` is specified on the command line.

```yaml $(tag) == '2022-12-01'
```

### Tag: package-2022-12-01

```yaml $(tag) == 'package-2022-12-01'
```