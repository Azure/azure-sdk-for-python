from azure.keyvault.certificates import CertificatePolicy

def test_policy_expected_errors():
    try:
        cert_policy = CertificatePolicy("issuer-name", "subject-name")
        assert False, "Error should've thrown since we only have one positional parameter"
    except TypeError as e:
        if '__init__' not in str(e):
            raise

    try:
        cert_policy = CertificatePolicy("issuer-name")
        assert False, "Error should be thrown since we haven't set a subject_name or sans"
    except ValueError as e:
        if "subject_name" not in str(e):
            raise