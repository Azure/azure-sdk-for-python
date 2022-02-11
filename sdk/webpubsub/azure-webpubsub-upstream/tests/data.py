import json

claims = {
    "iat": ["1632476178"],
    "nbf": ["1632476178"],
    "exp": ["1632476178"],
}

query = {
    "access_token": "ABC.DEF.GHI"
}

subprotocols = ["protocol1", "protocol2"]

client_certificates = [{
    "thumbprint": "ABC"
}]

body = json.dumps({
    "claims": claims,
    "query": query,
    "subprotocols": subprotocols,
    "clientCertificates": client_certificates
})

print(body)