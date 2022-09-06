# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os

TEST_PROXY_CERT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", 'eng', 'common', 'testproxy', 'dotnet-devcert.crt'))

# Duplicate certificate from KeyVault.
# https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/tests/ca.crt
USER_CERTIFICATE_PUBLIC_KEY = """-----BEGIN CERTIFICATE-----
MIIDazCCAlOgAwIBAgIUYju9zymmCCF7rCaROzfZs0pNgmkwDQYJKoZIhvcNAQEL
BQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0xOTA4MjgyMjU0MTNaFw0xOTA5
MjcyMjU0MTNaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw
HwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggEiMA0GCSqGSIb3DQEB
AQUAA4IBDwAwggEKAoIBAQD0YrMz5atoPmTTxLtCO69kM3E97bdjJgyAVZJS9mP3
HQyHkFNb09eDeAAzcZLR5nYXX7yweowTWVcIe3k9+Z/tUeVrAlOVe2COaIHAUZIh
jELq/u8257/8MqqbKXhsyrWNAVDyKndDgvbbgxNsUTbMoAe9BCL/5fzowsnPLaCI
MCYRaQJUySbIoTmKi11hF09CFFSkL9nvfQODFyEde6JHPWrVRse2lioPLJeC9LoU
GNNZnbqry+UbHp4vORPp6OQTqBTm1ZVWPzCuYuWUmEe27K7zghEJr/Yx0OLq9kI5
H960CSOkdhsOTcBkORfhivSQnmOn2RnCPIEsUTzjwXNZAgMBAAGjUzBRMB0GA1Ud
DgQWBBQIAunu6y1BmFSDfFNfTnqFggB0gzAfBgNVHSMEGDAWgBQIAunu6y1BmFSD
fFNfTnqFggB0gzAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQAr
+RM7gbqWRXnWJwE/hV/ZI2hXAhDN4RYQ4fWMJfg/E9wcLeqqRtJhXbqpJW08IZWp
QKcWfrFcfZ3ZxVAi5Ey+iuvD2VeBf9v5RZI4c9JqswS9xG2A1x/BeGcUk1y/q9E5
4whf5fLSJQVxK+C53yemoHPrBg8zVhLJv5SG7Uw7jcqiQvu2aHGGWPLiO7mmMPtP
qO/I+6FjXuBpNomTqM897MY3Qzg43rpoCilpOpkRtMHknfhFxt05p+Fn73Fb60ru
ZsFRA52lsEBxGmI0QmXGjwkUZFwQTXEDUWwId3VJxoHRZwv1gmHfwhkYt+mNWJDa
mU7AMDzlQRwGC8hpWJRT
-----END CERTIFICATE-----"""

# https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/tests/ca.key
USER_CERTIFICATE_PRIVATE_KEY = ("-----BEGIN RSA PRIVATE KEY-----\n"  #[SuppressMessage("Microsoft.Security", "CS001:SecretInline", Justification="Test secret that is found elsewhere in this repo")]
"""MIIEpQIBAAKCAQEA9GKzM+WraD5k08S7QjuvZDNxPe23YyYMgFWSUvZj9x0Mh5BT
W9PXg3gAM3GS0eZ2F1+8sHqME1lXCHt5Pfmf7VHlawJTlXtgjmiBwFGSIYxC6v7v
Nue//DKqmyl4bMq1jQFQ8ip3Q4L224MTbFE2zKAHvQQi/+X86MLJzy2giDAmEWkC
VMkmyKE5iotdYRdPQhRUpC/Z730DgxchHXuiRz1q1UbHtpYqDyyXgvS6FBjTWZ26
q8vlGx6eLzkT6ejkE6gU5tWVVj8wrmLllJhHtuyu84IRCa/2MdDi6vZCOR/etAkj
pHYbDk3AZDkX4Yr0kJ5jp9kZwjyBLFE848FzWQIDAQABAoIBAHrhegv5SrOy083r
mODX0/wFJcam1dRD2HtbC6UtgNxLPfaYKmH85duUJj23uMRUJkLgf6cZJ3+/J1T7
iN4Ru0mAKWQiGlcKX2WbxMon+dtmhGtW3n90DgPIkiJMuuGxF5Kb+9CYa7mFi4ya
ntSTDYPcX6e6AcM8KGv9La4/2f0/hQKCN3jZbnQ/GqjnJdxrAV1KV0IMoNPpZmat
Sa0EZ9eiR57/xAe1OxceEt0nO7hAl+jX7tFEGvaNClKG2OMgZ+oHOxI+s9jW8DyD
wRJbd0hxUl/KXLxzyeFTBdLxB+SQtlcr4w5khyt3AvlKd4Iveqkq2FBCtfATYitt
+Ic61IUCgYEA/j4mMdo+qokzACmGJWEquC6yNoUI5aYsHTRVvX0sLpBX7MapIEwM
zHdvMEFBxw8rs7ll1xELW+dnbIZqj/ou43E3+PSgovdFGOA8kQlPpcIIutTEZQh7
dlWzvAVZr0iO4xfXY2gFQot41fY4yRy8Q14ayo/VjQK4uKlnGqqlmwsCgYEA9hMc
FIAYpit7779tKD+O4vEkMoTkIxqSAZUuOZ5qB5UaF4Y/+MIGZUnrjJlGLnoFQmsP
CVPVMOQKV7yjg0LBadeDHEjESwHJNk0qxPSXWuXGlu01yVkqUehNumSBdnSLBmjR
jNIxPVEmW9d6+eAzIFiTkwqM9cAuLb75DL++iasCgYEAxhqzNEE0dzl0zfmNF29B
FEb+glDi/96dnRv8eywf0yCSAmNBwXLAvkmKD/WpRWxixyX9XrlfOntzMTMDsbBl
/L9pt8kVqiY2Zw3C49h3gVdR6hKD/Z3AZhKdfDJHEbfd7sHTCRgykQmQXFgBI2QK
pguboJ627atjODB3sGWrqMUCgYEA2QoJ3lsNYqM/8TpaQQGuOaSPVK+5uOyakyLN
XqzGwGFWXiFfEz2u/m+wfpZCPIQLV4WuAYAbrb+1D6WmYwPiLESVs8DKwY2Vt3tg
mc9SIC5CdqRKqIkoto264Qf82En6xXB2Q0qxe2+z8ZWhNfv1nDYEE9FeevNCx76F
VCVbHXkCgYEA4+FD1q6iwl9wsAOKFVo+W044/MhKHDsyIED3YOzeRTAWRl2w/KX0
c5ty2KecGu0cVXoAv2YUttHsuMZfm/QdosZr9UB4CR2lmzRys3LSx6QzCkZeMb/s
QOMs6SYCPXggdXCAu9EVf5+TtYQg7aQNTTuYErlyq2g/tk3un8bHTwI=
-----END RSA PRIVATE KEY-----""")

USER_CERTIFICATE = f"{USER_CERTIFICATE_PUBLIC_KEY}\n{USER_CERTIFICATE_PRIVATE_KEY}"

USER_CERTIFICATE_THUMBPRINT = "5F:23:3D:26:E2:28:88:9C:06:E0:88:21:FA:C7:B2:9A:F8:81:30:6B:F9:15:41:F2:34:05:05:44:4C:AD:5A:B5"
