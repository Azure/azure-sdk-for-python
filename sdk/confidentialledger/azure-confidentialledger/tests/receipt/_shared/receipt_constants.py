# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.confidentialledger.receipt._receipt_models import (
    LeafComponents,
    ProofElement,
    Receipt,
)


def get_test_valid_service_certificate_1():
    return """
-----BEGIN CERTIFICATE-----
MIIBejCCASCgAwIBAgIQcmv2rRjksVYvqdOOHxp5UjAKBggqhkjOPQQDAjAWMRQw
EgYDVQQDDAtDQ0YgTmV0d29yazAeFw0yMjExMDExODU0MzNaFw0yMzAxMzAxODU0
MzJaMBYxFDASBgNVBAMMC0NDRiBOZXR3b3JrMFkwEwYHKoZIzj0CAQYIKoZIzj0D
AQcDQgAEEFi2//FtAFoJvS+4jzQte+hjhhtBee8yjZ28ntukjeqWbG8XCncx4e0j
eoQbFmGC9BnMb+t3t6FskQZkvgobrqNQME4wDAYDVR0TBAUwAwEB/zAdBgNVHQ4E
FgQUQgzYFOQLy0vDkm3wqLSlcJsbQm8wHwYDVR0jBBgwFoAUQgzYFOQLy0vDkm3w
qLSlcJsbQm8wCgYIKoZIzj0EAwIDSAAwRQIhAN/DrvHLpwRa7PeuN7q4ZztPjEY6
R8r2IuT+wd5lMe7UAiAu7FftNooRjWIJ6pVFQO1xPtjCI5/JyvBUcJqfWT+Q2g==
-----END CERTIFICATE-----
"""


def get_test_valid_service_certificate_2():
    return """
-----BEGIN CERTIFICATE-----
MIIBezCCASGgAwIBAgIRAL1K5p7mE+zOdNn4Po05mDcwCgYIKoZIzj0EAwIwFjEU
MBIGA1UEAwwLQ0NGIE5ldHdvcmswHhcNMjIxMDI1MTIzMDU3WhcNMjMwMTIzMTIz
MDU2WjAWMRQwEgYDVQQDDAtDQ0YgTmV0d29yazBZMBMGByqGSM49AgEGCCqGSM49
AwEHA0IABGd51KunQeso9Y/6oA2p9Vh8Wf5eYCNPm8MTwE+1hVYX51U/LqdoVxZB
JvcWNbDkToOyxPdmFC19QmSb49pjfLGjUDBOMAwGA1UdEwQFMAMBAf8wHQYDVR0O
BBYEFErYKi5W20k63JsLMj3ZG/f/PaZwMB8GA1UdIwQYMBaAFErYKi5W20k63JsL
Mj3ZG/f/PaZwMAoGCCqGSM49BAMCA0gAMEUCIQC215NRdXWKaVNH9Rp2VJzMHHwN
qsUPm+U8mwLeOOk7TgIgL7JFqyJmnigevF2Ju/k4QkkBMZm4McuywM1f2n8+8Qk=
-----END CERTIFICATE-----
"""


def get_test_valid_receipt_1():
    return Receipt(
        cert="-----BEGIN CERTIFICATE-----\nMIIB0zCCAXqgAwIBAgIRALXhnOIN/WoLnD69pfR2rvQwCgYIKoZIzj0EAwIwFjEU\nMBIGA1UEAwwLQ0NGIE5ldHdvcmswHhcNMjIxMTAxMTg1NDM2WhcNMjMwMTMwMTg1\nNDM1WjATMREwDwYDVQQDDAhDQ0YgTm9kZTBZMBMGByqGSM49AgEGCCqGSM49AwEH\nA0IABAUkp7vj54d1qr51leVMEwn/GXFozJQ1Ycx+AYoCb++0a6lrekGEgN91dR6D\nYdaBRKbYPMphAf4vDQEcVIjpFwKjgaswgagwCQYDVR0TBAIwADAdBgNVHQ4EFgQU\n54/ExTbNk7ZnZWImu6xq+8vOngEwHwYDVR0jBBgwFoAUQgzYFOQLy0vDkm3wqLSl\ncJsbQm8wWwYDVR0RBFQwUocECvACNYIRYXAtc3RhZ2luZy1sZWRnZXKCN2FwLXN0\nYWdpbmctbGVkZ2VyLmNvbmZpZGVudGlhbC1sZWRnZXItc3RhZ2luZy5henVyZS5j\nb20wCgYIKoZIzj0EAwIDRwAwRAIgBkB5XGxiiB5hhyWuHrM5TDlLfDUNR4GV1vie\ntpmGmLsCIF76tqizqk+s5Wuoa8ePLvGxUXIy3Q+H2rfRFi2LIB0B\n-----END CERTIFICATE-----\n",
        nodeId="708c2e71b2533e5eb38e05cc344390d133c8fb336cb80481ab4e5e902e6131a5",
        serviceEndorsements=[],
        leafComponents=LeafComponents(
            claimsDigest="0000000000000000000000000000000000000000000000000000000000000000",
            commitEvidence="ce:2.35:fa08b4eae4a034971b97f0b21810951ec64b06fb2f4b5a1e80f6f4b83a23c719",
            writeSetDigest="fef1aa22972daba05864a7e986c1bb94aa6b8fea43781cb48907c972e9761e71",
        ),
        proof=[
            ProofElement(
                left="5e949d6d17b88900aeb8fb292f041075272d3b58108f2016a3ceea2a47ffad8f"
            ),
            ProofElement(
                left="fb199f029ed1e7886ca95f8ecb4f9a56edede5f15fb425874c2a34861a9765ee"
            ),
            ProofElement(
                left="efe9c61961fc189e292edeadb4317040ea4a6e5abc8cf349dc74295930ed7435"
            ),
        ],
        signature="MEYCIQC05OyTn/a5ZKphfY4AsnnBF2Rfj0j0pNrfPtHHO5JvnwIhAPItujuzkC8enmxIsG2X82hBgHCaNoFHL9GC3XfejOUI",
    )


def get_test_valid_receipt_2():
    return Receipt(
        cert="-----BEGIN CERTIFICATE-----\nMIIBzzCCAXWgAwIBAgIQIqJhTJJl+Oxf8Fl0oH622TAKBggqhkjOPQQDAjAWMRQw\nEgYDVQQDDAtDQ0YgTmV0d29yazAeFw0yMjEwMjUxMjMwNTZaFw0yMzAxMjMxMjMw\nNTVaMBMxETAPBgNVBAMMCENDRiBOb2RlMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcD\nQgAEqmsG0x22ZuFBjDItZruC+jVJza8qpXh/HKeX5yG/0/HKyjMOEce2g/C7Z/fi\nbf/bYXiCbz4WP/YbU3crQUtc7qOBpzCBpDAJBgNVHRMEAjAAMB0GA1UdDgQWBBSY\nw8oZLUv/qjpB/u0uaJyEGsMM9zAfBgNVHSMEGDAWgBRK2CouVttJOtybCzI92Rv3\n/z2mcDBXBgNVHREEUDBOghNhcC10ZXN0LWxlZGdlci1wcml2gjFhcC10ZXN0LWxl\nZGdlci1wcml2LmNvbmZpZGVudGlhbC1sZWRnZXIuYXp1cmUuY29thwQK8Eq3MAoG\nCCqGSM49BAMCA0gAMEUCIQCbokInYEKX7ItmjJDlnG/0EbIwgcCCGnRubIzHYhiX\n8gIgbqhPG68pxR43ZhJy6y6JeWuB+kSXsqRmQdYP3UMkzXg=\n-----END CERTIFICATE-----\n",
        leafComponents=LeafComponents(
            claimsDigest="0000000000000000000000000000000000000000000000000000000000000000",
            commitEvidence="ce:16.7415:e718636e480d0ea56650406cece0abf6c010f58e6635dce8f404e2d2779fbc9d",
            writeSetDigest="4242b251a0800c9b6857b5da503d92a152e43da79f3da20758f9c5db65d8dd4c",
        ),
        nodeId="a16d14661618d220365594fc4986f4401ff74785b70818b00e6590bb3c1a1a5d",
        proof=[
            ProofElement(
                left="113d89bdcb5282bf773ca12ba97a7baa1b2515a5ffecdb9feaae67bddc89c639"
            ),
            ProofElement(
                left="5f8edd797d0146b76e0ebfa6ee9d5e34a8f8b9795f3957202b3f92817b991918"
            ),
            ProofElement(
                left="7e00bfbb86030ac74e8db5b08af1a9dbe15659c083cdcedc78fc915ecd57ab3e"
            ),
            ProofElement(
                left="842e1dd9cb8768f9c158e61a51041d94c5a52c7a905068c85b6c5cc165010417"
            ),
            ProofElement(
                left="2921ba478d7cbfb8964b1b0221a6909ef8793738045d24c095200fa88396fa1b"
            ),
            ProofElement(
                left="65fa347e5392b4a1b399194321446ff7e0b25fc44609c9ddff2558674cc8b8fe"
            ),
            ProofElement(
                left="96736d241bfd0890cdbefdca97633f13cb345e18d62464ca4d3aeb4c4e2acc05"
            ),
            ProofElement(
                left="75fdb2b7f6589d7f38218dcdf09ad06d1873cc11692ac11ca099956c4d0df2c6"
            ),
            ProofElement(
                left="7cb66ee49ecb284ad967be5ae9f735e9046ebe5fb49bd093e29b851932afcac7"
            ),
            ProofElement(
                left="b5acc41d51ebc21112882d9e444dffcddc1135a6a1edd9b287ec6927e7baac84"
            ),
        ],
        serviceEndorsements=[],
        signature="MEUCIBehRsSl0CyNwMHiObY3Kxw9cV5e/rSQKmCrEJooxWvmAiEAnYwaT5yVGFkSFuJ8JdbW0ZolbDHzRrfl+fm6jIrDzxw=",
    )


def get_test_valid_receipt_1_dict():
    return {
        "is_signature_transaction": False,
        "cert": "-----BEGIN CERTIFICATE-----\nMIIB0zCCAXqgAwIBAgIRALXhnOIN/WoLnD69pfR2rvQwCgYIKoZIzj0EAwIwFjEU\nMBIGA1UEAwwLQ0NGIE5ldHdvcmswHhcNMjIxMTAxMTg1NDM2WhcNMjMwMTMwMTg1\nNDM1WjATMREwDwYDVQQDDAhDQ0YgTm9kZTBZMBMGByqGSM49AgEGCCqGSM49AwEH\nA0IABAUkp7vj54d1qr51leVMEwn/GXFozJQ1Ycx+AYoCb++0a6lrekGEgN91dR6D\nYdaBRKbYPMphAf4vDQEcVIjpFwKjgaswgagwCQYDVR0TBAIwADAdBgNVHQ4EFgQU\n54/ExTbNk7ZnZWImu6xq+8vOngEwHwYDVR0jBBgwFoAUQgzYFOQLy0vDkm3wqLSl\ncJsbQm8wWwYDVR0RBFQwUocECvACNYIRYXAtc3RhZ2luZy1sZWRnZXKCN2FwLXN0\nYWdpbmctbGVkZ2VyLmNvbmZpZGVudGlhbC1sZWRnZXItc3RhZ2luZy5henVyZS5j\nb20wCgYIKoZIzj0EAwIDRwAwRAIgBkB5XGxiiB5hhyWuHrM5TDlLfDUNR4GV1vie\ntpmGmLsCIF76tqizqk+s5Wuoa8ePLvGxUXIy3Q+H2rfRFi2LIB0B\n-----END CERTIFICATE-----\n",
        "node_id": "708c2e71b2533e5eb38e05cc344390d133c8fb336cb80481ab4e5e902e6131a5",
        "service_endorsements": [],
        "leaf_components": {
            "claims_digest": "0000000000000000000000000000000000000000000000000000000000000000",
            "commit_evidence": "ce:2.35:fa08b4eae4a034971b97f0b21810951ec64b06fb2f4b5a1e80f6f4b83a23c719",
            "write_set_digest": "fef1aa22972daba05864a7e986c1bb94aa6b8fea43781cb48907c972e9761e71",
        },
        "proof": [
            {
                "left": "5e949d6d17b88900aeb8fb292f041075272d3b58108f2016a3ceea2a47ffad8f",
            },
            {
                "left": "fb199f029ed1e7886ca95f8ecb4f9a56edede5f15fb425874c2a34861a9765ee",
            },
            {
                "left": "efe9c61961fc189e292edeadb4317040ea4a6e5abc8cf349dc74295930ed7435",
            },
        ],
        "signature": "MEYCIQC05OyTn/a5ZKphfY4AsnnBF2Rfj0j0pNrfPtHHO5JvnwIhAPItujuzkC8enmxIsG2X82hBgHCaNoFHL9GC3XfejOUI",
    }


def get_test_valid_receipt_2_dict():
    return {
        "cert": "-----BEGIN CERTIFICATE-----\nMIIBzzCCAXWgAwIBAgIQIqJhTJJl+Oxf8Fl0oH622TAKBggqhkjOPQQDAjAWMRQw\nEgYDVQQDDAtDQ0YgTmV0d29yazAeFw0yMjEwMjUxMjMwNTZaFw0yMzAxMjMxMjMw\nNTVaMBMxETAPBgNVBAMMCENDRiBOb2RlMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcD\nQgAEqmsG0x22ZuFBjDItZruC+jVJza8qpXh/HKeX5yG/0/HKyjMOEce2g/C7Z/fi\nbf/bYXiCbz4WP/YbU3crQUtc7qOBpzCBpDAJBgNVHRMEAjAAMB0GA1UdDgQWBBSY\nw8oZLUv/qjpB/u0uaJyEGsMM9zAfBgNVHSMEGDAWgBRK2CouVttJOtybCzI92Rv3\n/z2mcDBXBgNVHREEUDBOghNhcC10ZXN0LWxlZGdlci1wcml2gjFhcC10ZXN0LWxl\nZGdlci1wcml2LmNvbmZpZGVudGlhbC1sZWRnZXIuYXp1cmUuY29thwQK8Eq3MAoG\nCCqGSM49BAMCA0gAMEUCIQCbokInYEKX7ItmjJDlnG/0EbIwgcCCGnRubIzHYhiX\n8gIgbqhPG68pxR43ZhJy6y6JeWuB+kSXsqRmQdYP3UMkzXg=\n-----END CERTIFICATE-----\n",
        "leafComponents": {
            "claimsDigest": "0000000000000000000000000000000000000000000000000000000000000000",
            "commitEvidence": "ce:16.7415:e718636e480d0ea56650406cece0abf6c010f58e6635dce8f404e2d2779fbc9d",
            "writeSetDigest": "4242b251a0800c9b6857b5da503d92a152e43da79f3da20758f9c5db65d8dd4c",
        },
        "nodeId": "a16d14661618d220365594fc4986f4401ff74785b70818b00e6590bb3c1a1a5d",
        "proof": [
            {
                "left": "113d89bdcb5282bf773ca12ba97a7baa1b2515a5ffecdb9feaae67bddc89c639"
            },
            {
                "left": "5f8edd797d0146b76e0ebfa6ee9d5e34a8f8b9795f3957202b3f92817b991918"
            },
            {
                "left": "7e00bfbb86030ac74e8db5b08af1a9dbe15659c083cdcedc78fc915ecd57ab3e"
            },
            {
                "left": "842e1dd9cb8768f9c158e61a51041d94c5a52c7a905068c85b6c5cc165010417"
            },
            {
                "left": "2921ba478d7cbfb8964b1b0221a6909ef8793738045d24c095200fa88396fa1b"
            },
            {
                "left": "65fa347e5392b4a1b399194321446ff7e0b25fc44609c9ddff2558674cc8b8fe"
            },
            {
                "left": "96736d241bfd0890cdbefdca97633f13cb345e18d62464ca4d3aeb4c4e2acc05"
            },
            {
                "left": "75fdb2b7f6589d7f38218dcdf09ad06d1873cc11692ac11ca099956c4d0df2c6"
            },
            {
                "left": "7cb66ee49ecb284ad967be5ae9f735e9046ebe5fb49bd093e29b851932afcac7"
            },
            {
                "left": "b5acc41d51ebc21112882d9e444dffcddc1135a6a1edd9b287ec6927e7baac84"
            },
        ],
        "serviceEndorsements": [],
        "signature": "MEUCIBehRsSl0CyNwMHiObY3Kxw9cV5e/rSQKmCrEJooxWvmAiEAnYwaT5yVGFkSFuJ8JdbW0ZolbDHzRrfl+fm6jIrDzxw=",
    }
