### Settings

```yaml
input-file: {{ input_file }}
output-folder: ../
namespace: {{ namespace }}
package-name: {{ package_name }}
license-header: MICROSOFT_MIT_NO_VERSION
title: {{ client_name }}
package-version: 1.0.0b1
package-mode: dataplane
{%- if security_scope %}
security: AADToken
security-scopes: {{ security_scope }}
{%- elif security_header_name %}
security: AzureKey
security-header-name: {{ security_header_name }}
{%- endif %}
```
