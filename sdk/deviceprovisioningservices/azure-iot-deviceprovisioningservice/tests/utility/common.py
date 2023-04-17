from base64 import b32encode, b64decode, b64encode
from math import ceil
from os import makedirs, urandom
from os.path import exists

CERT_NAME = "sdk_test_certificate"
CERT_ENDING = "-cert.pem"
KEY_ENDING = "-key.pem"


def create_random_name(prefix="dps_sdk_test", length=24):
    if len(prefix) > length:
        raise ValueError(
            "The length of the prefix must not be longer than random name length"
        )

    padding_size = length - len(prefix)
    if padding_size < 4:
        raise ValueError(
            "The randomized part of the name is shorter than 4, which may not be able to offer enough "
            "randomness"
        )

    random_bytes = urandom(int(ceil(float(padding_size) / 8) * 5))
    random_padding = b32encode(random_bytes)[:padding_size]

    return str(prefix + random_padding.decode().lower())


def generate_attestation(
    attestation_type,
    endorsement_key=None,
    primary_key=None,
    secondary_key=None,
    primary_cert=None,
    secondary_cert=None,
    signing_certs=False,
):
    attestation = {"type": attestation_type}
    if attestation_type == "tpm":
        attestation["tpm"] = {"endorsementKey": endorsement_key}
    if attestation_type == "symmetricKey":
        attestation["symmetricKey"] = {
            "primaryKey": primary_key,
            "secondaryKey": secondary_key,
        }
    if attestation_type == "x509":
        if primary_cert:
            primary_cert = {"certificate": primary_cert}
        if secondary_cert:
            secondary_cert = {"certificate": secondary_cert}
        certs = (
            {"primary": primary_cert, "secondary": secondary_cert}
            if (primary_cert or secondary_cert)
            else None
        )
        attestation["x509"] = (
            {"signingCertificates": certs}
            if signing_certs
            else {"clientCertificates": certs}
        )
    return attestation


def generate_enrollment(
    id=None,
    attestation_type=None,
    capabilities=None,
    endorsement_key=None,
    primary_cert=None,
    secondary_cert=None,
    device_id=None,
    iot_hub_host_name=None,
    initial_twin_properties=None,
    provisioning_status=None,
    reprovision_policy=None,
    primary_key=None,
    secondary_key=None,
    allocation_policy=None,
    iot_hubs=None,
    webhook_url=None,
    api_version=None,
    optional_device_information=None,
):
    attestation = generate_attestation(
        attestation_type=attestation_type,
        endorsement_key=endorsement_key,
        primary_key=primary_key,
        secondary_key=secondary_key,
        primary_cert=primary_cert,
        secondary_cert=secondary_cert,
    )
    custom_allocation = (
        {"webhookUrl": webhook_url, "apiVersion": api_version}
        if allocation_policy == "custom"
        else None
    )
    enrollment = {
        "registrationId": id or create_random_name(),
        "attestation": attestation,
        "allocationPolicy": allocation_policy,
        "capabilities": capabilities,
        "reprovisionPolicy": reprovision_policy,
        "customAllocationDefinition": custom_allocation,
        "provisioningStatus": provisioning_status,
        "deviceId": device_id,
        "optionalDeviceInformation": optional_device_information,
        "iotHubs": iot_hubs,
        "iotHubHostName": iot_hub_host_name,
        "initialTwin": initial_twin_properties,
    }
    return enrollment


def generate_enrollment_group(
    id=None,
    attestation_type=None,
    capabilities=None,
    endorsement_key=None,
    primary_cert=None,
    secondary_cert=None,
    iot_hub_host_name=None,
    initial_twin_properties=None,
    provisioning_status=None,
    reprovision_policy=None,
    primary_key=None,
    secondary_key=None,
    allocation_policy=None,
    iot_hubs=None,
    webhook_url=None,
    api_version=None,
):
    attestation = generate_attestation(
        attestation_type=attestation_type,
        endorsement_key=endorsement_key,
        primary_key=primary_key,
        secondary_key=secondary_key,
        primary_cert=primary_cert,
        secondary_cert=secondary_cert,
        signing_certs=True,
    )
    custom_allocation = (
        {"webhookUrl": webhook_url, "apiVersion": api_version}
        if allocation_policy == "custom"
        else None
    )

    return {
        "enrollmentGroupId": id or create_random_name(),
        "attestation": attestation,
        "allocationPolicy": allocation_policy,
        "capabilities": capabilities,
        "provisioningStatus": provisioning_status,
        "reprovisionPolicy": reprovision_policy,
        "iotHubs": iot_hubs,
        "iotHubHostName": iot_hub_host_name,
        "initialTwin": initial_twin_properties,
        "customAllocationDefinition": custom_allocation,
    }


def generate_key(byte_length=32):
    """
    Generate cryptographically secure device key.
    """
    import secrets

    token_bytes = secrets.token_bytes(byte_length)
    return b64encode(token_bytes).decode("utf8")


def create_test_cert(
    subject=CERT_NAME,
):
    return create_self_signed_certificate(
        subject=subject,
        valid_days=1,
    )


def create_self_signed_certificate(
    subject: str,
    valid_days: int = 365,
    key_size: int = 2048,
):
    """
    Function used to create a basic self-signed certificate with no extensions.

    Args:
        subject (str): Certificate common name; host name or wildcard.
        valid_days (int): number of days certificate is valid for; used to calculate
            certificate expiry.
        cert_putput_dir (str): string value of output directory.
        cert_only (bool): generate certificate only; no private key or thumbprint.
        file_prefix (str): Certificate file name if it needs to be different from the subject.
        sha_version (int): The SHA version to use for generating the thumbprint. For
            IoT Hub, SHA1 is currently used. For DPS, SHA256 has to be used.

    Returns:
        result (dict): dict with certificate value, private key and thumbprint.
    """
    import datetime

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    # create a key pair
    key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    serial = x509.random_serial_number()
    # create a self-signed cert
    subject_name = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, subject),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject_name)
        .issuer_name(subject_name)
        .public_key(key.public_key())
        .serial_number(serial)
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=valid_days)
        )
    )

    # sign
    cert = cert.sign(key, hashes.SHA256())

    # private key
    key_dump = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    # certificate string
    cert_dump = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    hash = hashes.SHA256()

    # thumbprint
    thumbprint = cert.fingerprint(hash).hex().upper()

    result = {
        "certificate": cert_dump.rstrip(),
        "privateKey": key_dump,
        "thumbprint": thumbprint,
    }

    return result


def write_content_to_file(
    content,
    destination: str,
    file_name: str,
    overwrite: bool = False,
):
    from pathlib import PurePath

    dest_path = PurePath(destination)
    file_path = dest_path.joinpath(file_name)

    if exists(file_path) and not overwrite:
        raise f"File already exists at path: {file_path}"
    if overwrite and destination:
        makedirs(destination, exist_ok=True)
    write_content = bytes(content, "utf-8") if isinstance(content, str) else content
    with open(file_path, "wb") as f:
        f.write(write_content)


def open_certificate(certificate_path: str) -> str:
    """
    Opens certificate file (as read binary) from the file system and
    returns the value read.

    Args:
        certificate_path (str): the path the the certificate file.

    Returns:
        certificate (str): returns utf-8 encoded value from certificate file.
    """
    certificate = ""
    with open(certificate_path, "rb") as cert_file:
        certificate = cert_file.read()
        try:
            certificate = certificate.decode("utf-8")
        except UnicodeError:
            certificate = b64encode(certificate).decode("utf-8")
    # Remove trailing white space from the certificate content
    return certificate.rstrip()


def sign_string(key, string_to_sign, key_is_base64=True):
    """
    Compute device SAS key
    Args:
        primary_key: Primary group SAS token to compute device keys
        registration_id: Registration ID is alphanumeric, lowercase, and may contain hyphens.
    Returns:
        device key
    """
    import hashlib
    import hmac

    if key_is_base64:
        key = b64decode(key)
    else:
        if isinstance(key, str):
            key = key.encode("utf-8")
    if isinstance(string_to_sign, str):
        string_to_sign = string_to_sign.encode("utf-8")
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    digest = signed_hmac_sha256.digest()
    encoded_digest = b64encode(digest)
    return encoded_digest
