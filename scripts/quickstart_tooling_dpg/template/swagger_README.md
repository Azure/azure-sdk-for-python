### Settings

```yaml
input-file: {{ input_file }}
output-folder: {{ swagger_readme_output }}
namespace: {{ namespace }}
package-name: {{ package_name }}
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
title: {{ client_name }}
version-tolerant: true
package-version: 1.0.0b1
{%- if security_scope %}
security: AADToken
security-scopes: {{ security_scope }}
{%- elif security_header_name %}
security: AzureKey
security-header-name: {{ security_header_name }}
{%- endif %}
```
