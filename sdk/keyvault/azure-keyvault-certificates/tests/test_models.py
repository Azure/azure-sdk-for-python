from azure.keyvault.certificates import CertificatePolicy

def test_policy_expected_errors():
    try:
        cert_policy = CertificatePolicy("issuer-name", "subject-name")
        assert False, "Error should've thrown since we only have one positional parameter"
    except TypeError as e:
        if str(e) == '__init__() takes 2 positional arguments but 3 were given':
            pass
        else:
            raise e

    try:
        cert_policy = CertificatePolicy("issuer-name")
        assert False, "Error should be thrown since we haven't set a subject_name or sans"
    except ValueError as e:
        if str(e) == "You need to set either subject_name or one of the subject alternative names parameters":
            pass
        else:
            raise e