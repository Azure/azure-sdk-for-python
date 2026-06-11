# Contoso.WidgetManager

## Configuration

Testing buildState

### Basic Information

```yaml
openapi-type: data-plane
tag: tag-1
```

### Tag: tag-1

These settings apply only when `--tag=tag-1` is specified on the command line.

```yaml $(tag) == 'tag-1'
input-file:
  - a.json
```

### Tag: tag-2

These settings apply only when `--tag=tag-2` is specified on the command line.

```yaml $(tag) == 'tag-2'
input-file:
  - e.json
```

### Tag: tag-3

These settings apply only when `--tag=tag-3` is specified on the command line.

This tag has no yaml entities defined.

```yaml $(tag) == 'tag-3'

```
