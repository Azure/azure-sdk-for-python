# Using the CertificateCredential

Applications which execute in a protected environment can authenticate using a client assertion signed by a private key whose public key or root certificate is registered with AAD. The Azure.Identity library provides the `CertificateCredential` for applications choosing to authenticate this way. Below are some examples of how applications can utilize the `CertificateCredential` to authenticate clients.


## Loading certificates from disk

Applications commonly need to load a client certificate from disk. One approach is for the application to construct the `CertificateCredential` by specifying the application's tenant ID, client ID, and the path to the certificate.

```py
credential = CertificateCredential(tenant_id, client_id, "./certs/cert.pfx")
```
Alternatively, the application can load the certificate itself, such as in the following example.

```py
certificate_data = open(CERT_PATH, "rb").read()

credential = CertificateCredential(tenant_id, client_id, certificate_data=certificate_data)
```

## Rolling certificates

Long running applications may have the need to roll certificates during process execution. Certificate rotation is not currently supported by the `CertificateCredential` which treats the certificate used to construct the credential as immutable. This means that any clients constructed with a `CertificateCredential` using a particular cert would fail to authenticate requests after that cert has been rolled and the original is no longer valid. 

However, if an application wants to roll this certificate without creating new service clients, it can accomplish this by creating its own `TokenCredential` implementation which wraps the `CertificateCredential`. The implementation of this custom credential `TokenCredential` would somewhat depend on how the application handles certificate rotation.

### Explicit rotation

If the application gets notified of certificate rotations and it can directly respond, it might choose to wrap the `CertificateCredential` in a custom credential which provides a means for rotating the certificate. 

```py
class RotatableCertificateCredential(object):
    def __init__(self, tenant_id, client_id, certificate_path=None, **kwargs):
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._credential = CertificateCredential(tenant_id, client_id, certificate_path, **kwargs)
    
    def get_token(self, *scopes, **kwargs):
        return self._credential.get_token(*scopes, **kwargs)

    def rotate_certificate(certificate_path, **kwargs):
        self._credential = CertificateCredential(self._tenant_id, self._client_id, certificate_path, **kwargs)
```

The above example shows a custom credential type `RotatableCertificateCredential` which provides a `rotate_certificate` method. The implementation internally relies on a `CertificateCredential` instance, `_credential`, and `rotate_certificate` simply replaces this instance with a new instance using the updated certificate.

### Implicit rotation
Some applications might want to respond to certificate rotations which are external to the application (for instance, if a separate process rotates the certificate by updating it on disk). Here the application create a custom credential which checks for certificate updates when tokens are requested. 

```py
class RotatingCertificateCredential(object):
    def __init__(self, tenant_id, client_id, certificate_path=None, **kwargs):
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._certificate_path = certificate_path
        self._certificate_last_modified = time.time()
        self.refresh_certificate()

    def get_token(self, *scopes, **kwargs):
        self.refresh_certificate()
        return self._credential.get_token(*scopes, **kwargs)

    def refresh_certificate():
        certificate_last_modified = os.path.getmtime(self._certificate_path)
        if self._certificate_last_modified < certificate_last_modified:
            self._certificate_last_modified = certificate_last_modified
            self._credential = CertificateCredential(tenant_id, client_id, self._certificate_path, **kwargs)
```

In this example the custom credential type `RotatingCertificateCredential` again uses a `CertificateCredential` instance, `_credential`, to retrieve tokens. However, in this case it will attempt to refresh the certificate prior to obtaining the token. The method `refresh_certificate` will query to see if the certificate has changed, and if so it will replace `_credential` with a new instance using the new certificate.