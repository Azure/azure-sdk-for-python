# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import json
import logging
import time

from azure.core.exceptions import ResourceExistsError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure_devtools.scenario_tests import RecordingProcessor, RequestUrlNormalizer
from azure.keyvault.certificates import (
    AdministratorContact,
    ApiVersion,
    CertificateClient,
    CertificateContact,
    CertificatePolicyAction,
    CertificatePolicy,
    KeyType,
    KeyCurveName,
    KeyUsageType,
    CertificateContentType,
    LifetimeAction,
    CertificateIssuer,
    IssuerProperties,
    parse_key_vault_certificate_id
)
from azure.keyvault.certificates._shared import HttpChallengeCache
from devtools_testutils import PowerShellPreparer
import pytest

from _shared.test_case import KeyVaultTestCase

KeyVaultPreparer = functools.partial(
    PowerShellPreparer,
    "keyvault",
    azure_keyvault_url="https://vaultname.vault.azure.net"
)


class RetryAfterReplacer(RecordingProcessor):
    """Replace the retry after wait time in the replay process to 0."""

    def process_response(self, response):
        if "retry-after" in response["headers"]:
            response["headers"]["retry-after"] = "0"
        return response


class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record)


class CertificateClientTests(KeyVaultTestCase):

    CERT_CONTENT_PASSWORD_ENODED = b"0\x82\t;\x02\x01\x030\x82\x08\xf7\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\x08\xe8\x04\x82\x08\xe40\x82\x08\xe00\x82\x06\t\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\x05\xfa\x04\x82\x05\xf60\x82\x05\xf20\x82\x05\xee\x06\x0b*\x86H\x86\xf7\r\x01\x0c\n\x01\x02\xa0\x82\x04\xfe0\x82\x04\xfa0\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x030\x0e\x04\x08\xf5\xe5\x81\xfd\xa4\xe19\xf0\x02\x02\x07\xd0\x04\x82\x04\xd8.\xb2>H\n\xee\xd9\xd0YE\x04e%\x8e\xd7Cr\xde.F\xa1\xd8W\x11Gw@L;!ght \r\xa8\x06\xb9\x10!\xdb\x0b\xc8\x00\x16g}\xaaa\x1dj\x91lK\x1e\x7f@\xa9x.\xdb\xb0\x04l\xe97\xe7\xeaHM\x96\xa2\xcb\xad\xd8`\x19$\xa5\x1f\xa9\r\xd9\xe0f\xdd}gC\xd6\xacl\x07\x12\xaes\xe8\x11\xd2\xd8b\xf2\xc8\xdf\x12H\xe0\x9bw0\xb3\xed\xb9c\xdf\xee\xc8e\x8a\x0c\x8f\x85\x8e>\x03\xa6\xfe\xd4:S\x8e\x12\x15g\xa4\xe3\xa407l\xde\x03\x88\xbd\xee\xfe\xdf\xb4\xd3g\xb3n\xe6\xb3\x9d\xa3\xa9\xf8N\xbd0=s\xfc2}\x92\x80c\x86\x8a%\xf6\x18Rl\x9c*9\xe7F]5\xdaWR\xdaS\xa4\x01!m\xfa[\xb8@&\xbb\xd8\x86:x\xfbQ\xb9\xd3\xc2\xbel\xd1\xbfjd-\x84\xba\xcfw\x08\xee\x89\x93\xf2q\xcf\xdc<\xa64\xea\x8blZ\xab\xe4\xed\x8c\xd5\x96\x1a,.\xb7C|m\xdd\xe5om\xc3\xe1\xdc\xdd<\x0fXG\x92\x1c\xff(4\xef\x91\x10\x10\xa6\xfa\xd6\xf0\x84\x8a\x9a\x00\xdd\x9b3y\xe4\xf7\xb9\xe7\x11\xdfIa\x81\xee\x03\xf0\xf2\xc6^k\x9e\xc8\xc4\\\xd6\x1d2\xb6\xca\xf4\xec\x96\x8a\x16\xa2\x8b&\x1b\x16\xa7a\x8d\x88\x1b\xf9\xe8\xdcF\xcf9`\xca\x8c\xf6x\x8aV\t{\x92I\xda)\xa6\x97\x13\xf3\xfbg\xb6\x10\xe0\x8a\xa42>\xed\xfc\xd0q\x1c\xf7=7w\x04\xaf\x9b\xb9\xd6|iu\xfcio\xe5:\x02\x92\xf1i\xb1f\x82\xa78\x90MY\xe4\xcdY\x01n\x82i-]\xf7O\x1c\x07q2\x18\xd4^\xa7\x86A\xdf0N\xf6x\x134\r5\xa7\xe8\xbf\t\x08\xec\x85\x7fe\x8a\x1a\xfb\xe4F\xa1\xf5Q\xdd\x96\xd1J M\x17\xa4\xc3\x8f\xfa\x97\x16\xdd07\xf0\x90\x9e\xc1\x80\x99\x00\x066#~\x0f\x89\x98\xee-\xb9v\xd4\xee\xfc\x97;;\x12\xdd\x84\x05\x05\xa4|\x89\xa7*\xd8X\xb7\xef:$\xb9Y\x80^\x101\xe4\x88\xf5\x1a\xff\xc7\x99H\xf071u\x99GTb\xb8;\xee6\xa3#r\xddRK\x07W\x004\xed\x17\xaf%\xfdD\xb5\x92\xc5:\xe7\xbf\x97H/\xba\x97-@\xfe\xeas\xf9~\xf5\xf8.\x07\xa3\xa5\xb4\xef\x9dc\xe5\x93\x13\xeb\x12\xa3\x1a\x1eiy\xee\xccV\xe7n\xc4\x8c\xd7\x8db2\xdd\x84\x9d\xd1\xf2\x13\xddM\x00\xe4\xd2\xc4\xbc\x9fk~Lz&!\xe3D\xbczW[j\xb2\xbbS\xe8\x1b\x06\xb6`\x90GU\x02$\xf2\xea\xb0\xa5C\xbc\x02\r\xc7w\x0f\x03\xf0\x86\xaa\xbeN_`FfP\"\x84i\x8d\xea~\xe0\xbf\xcc8;I4,\xf4\xc0{\x96\x1e~\x05\xcd\xdeoi\x13\xce\xbb7}F\xb4uYh\x9f\xd4V\x00\xcda-\xa3\xba\xc7\x9d\xe2\xbc;\xe9\x95\x8d\xe3V\xa4\xc7d\r\xd0\x94\x9e0\x9a\x87^\xa5s\xe8\x02\x9f\xcf\xc2\x02K\xf7E\x9cA\xb2\x04\xdaW\x88\xc4q\xad\x8f\xd0<\xa8\xbf\xc0\xe3p\xaa\xc6\xc3\xc5\x15\xbb\xbd\x94U*\xce\xfc\xa4\x19\x04\xd2K\x1aJ\x19Y\x93\x91\xa4y\xac\x83X/\xfb\x1e/\xcd\xa9Am\"Z\n\xf5pw\xa5\xa2\xf1\xa3P\xc6\xbb\x9a\xaah]\xf8\x8d\x97d\xb79\x17\xa7K\x99\xaa\x9a~\x15\xf2\x99j*/2;|\x17\xbc\x87\x08\xf9>-\x8aQ\xb1M\x82\xc9\xcfCV\x80\xc0\xea\xb2 \x7f\xeb\x84?\x88\xe9\xa6\x07\xa1\xb3\x1c\x93\xd2RGk\x1d\xad\xf3\xafQ\xda6\x1d\xb1|\x18Qx\xe0\xc0r\x15\xd2\xfa#\xed\xb2X<ae\x165\xce\xa7\xa6V\xf3\xab\x1c\xb0s9\xc5\xfb\x06B\x82\xb6\x16\x9f7\xf1T\xf7\xe1!\xc4\xd5\x95\xd4\xfe\x9b\x8c\xee\xbb\xe2DA\xd8[\xbd\xa9~\x98\x06eB\x0b@\xca!\xb93\xe7w\xcbE\xb4\t\x1b\xaeh\xcb\x0e\x8f\xa4\xf7\x1c{\x1dK\xe0\xa0T\xe24\xd5\xae\xab\xf7\x11\x8e\xbe\xf4\x14\xa3`\xb8\xc3\x13\"\xb8\x9d\xf8|\x1f\x99\xb4hk\x11\rY\xd2\xdc93^j\xc7\x04Gf\xbe\xdf\xb5\x10\xa2R\x83\xe6K+<\x91\xbaE\xd3@\xec\xed\xa9\xce\x9d\xe6\x89\xc0\xd8F\xcf\xfe\xb3o\x1c\x08\x8cN\xff\xf2\x7fw\x89\xec\x80zzE;\x82\xbb\x8f\x89\x9b\xd94a<6^\x0e\xf9og\x16*\xbcF\x9c5 \xc8\x89o4\xf6\x99L\x1ePl\xc8\x9d\xe3\x1e8\xfeQ4,\xb8\xbd\x91\xc3\xd0\x85\x18++N\xce\x9ez\xcc\x81\x9b\xd5\x1a;u\x08\xb1\xa1)K\xfb(W7\xc5]k\xd6\xbc\n\x92\x8b1\x9e\x81\xbd\xf6\x80\xa8M\x0bkz\x07\x17\xe6\xb2\x0c\x8cx$sR\x1d~Q\x89\x91\x9c\xdaX\xc9\x18TS\x89\xe1g\xb2\x9f=4\xf2.\x1dvK${\x9b\xdam\x9b7\xec\xb6\xfc\x8a\x08\x14`\xd0Xg!\xb3jZ\xee\x06\t\xd0\xc8\xae\x1f\xcf\x7f\x05i\xee'Y\x88\xf2\x8aWU~\x0c\xa8\xfd\xf0\x9e=\x1d\xa8\xbc\xe7\xe9\x87\x1fN@\x98\xbe3\xd0h\x16c\xeb\x02\x0f\xbc\x01\x10\xd9\xf9\x1f\xb9\xcb6.\x11\xcfY\xa1U\xfb\x9eJ{-1\x81\xdc0\r\x06\t+\x06\x01\x04\x01\x827\x11\x021\x000\x13\x06\t*\x86H\x86\xf7\r\x01\t\x151\x06\x04\x04\x01\x00\x00\x000W\x06\t*\x86H\x86\xf7\r\x01\t\x141J\x1eH\x00a\x008\x000\x00d\x00f\x00f\x008\x006\x00-\x00e\x009\x006\x00e\x00-\x004\x002\x002\x004\x00-\x00a\x00a\x001\x001\x00-\x00b\x00d\x001\x009\x004\x00d\x005\x00a\x006\x00b\x007\x0070]\x06\t+\x06\x01\x04\x01\x827\x11\x011P\x1eN\x00M\x00i\x00c\x00r\x00o\x00s\x00o\x00f\x00t\x00 \x00S\x00t\x00r\x00o\x00n\x00g\x00 \x00C\x00r\x00y\x00p\x00t\x00o\x00g\x00r\x00a\x00p\x00h\x00i\x00c\x00 \x00P\x00r\x00o\x00v\x00i\x00d\x00e\x00r0\x82\x02\xcf\x06\t*\x86H\x86\xf7\r\x01\x07\x06\xa0\x82\x02\xc00\x82\x02\xbc\x02\x01\x000\x82\x02\xb5\x06\t*\x86H\x86\xf7\r\x01\x07\x010\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x060\x0e\x04\x08\xd5\xfeT\xbd\x8c\xc7<\xd6\x02\x02\x07\xd0\x80\x82\x02\x88\xe6D\x13\xbe\x08\xf7\xd55C\xb4\xb3\xe0U\xbb\x08N\xce)\x00\x18\xd0f@sB\x86b\x7f\xa7,\xcfl\xc5\x1b\xc7\xbbN\xebw\x88U':\xee!\x11u\xad\x96\x08I\x95\xc0\xf8\xa0iT$=\xab\xa6\xb1\xfa|\xf8\xbe\xa2W\xf0L\x7f\x94J\x97$Ws\x08t\xbdGn\xd9\x06\xbb\xa9\xa7C\xfa\x01P\xdaI\xe0\x7f\x80\xe4\xea\xf6(\xdb\xfd\x87\xc5\xac\xae!\xfe\xa3\xa7\x07\xbc\xbe\xa9xq\xad\xd9\xb5e\xdf\xb9\x18\xb1\xd9\xfc \x96\xd34l\xcc\xf5\x83\x9f]\xef\x1f\xe0\x957\xcd\xab\x13e\xb2\xdc\xb4\x03\xfa\xd6\xac\xf2c5\xb3\x8fEM\x97\xcaB\xeesp-\x95;X\xb1\r\xf6f\xc9\xae\xeb\xb0;P\xd0p\xea\xd5m\x90E\xe5\x14:\xa1j\xf1!PC\xb7v\xf6*1\x8f\x90/\x1c\xe9f\x104\xab\x8e\x19g\xdf\xde\xc7E\xfa@\x01M+\x9c.[\x10\x9b\xba\x91\xd6\xb2\x0cQ\xc0\xa7\xed\xaf\x1c\xac\xcc\xc1\xec\x02\xf3h5\xc4\xe5\xa9\xc7-y\xef\x9ep\xdc\x13%\x06\xb5\xfc\xc0\xdb\x9e\x13\xba\xfe\xa1\xc0\xed\xc7\xc6\xd6\xa6\x03\xab\xc4\xe1\xeb~o\x18\xd3\x16\xd7\r\xecU.\xe5\xd2\xe1/u\xac\x80\xb0\x11\xd6M\xc3\x82\xda\xd9Lk\x96\xdf\x1e\xb8X\xf0\xe1\x08\xaa>[7\x91\xfdE\xd1r\xf0o\xd6\xdb\x7fm\x8c;\xb59\x88\xc1\x0f'b\x06\xac\xc1\x9f\xc1\xc6\xd44\xa3\xd4\xf8\xdc\xd2G\x7f\xf3gxeM7\xd3\xc2\x85L-\xf2\x19\xc4ZwA\xa7\x10}\x0e\x8bx\x84'\xd1\xdb\xae%\x1b}S\x1b\\\xd1\xce\x17\xe3$\xb5h\x83V\xac\xe7tc\n\x9a\xe2Ru\xf4\xc1*\xf1\x85\xbd\xe8\xc0YS\xb9\x13\x89\xa0.\xfa\x1a2f\xdc\x85\xcd\xc1;\xbb\x0bz\xb6\x87\x9c\x93y\x86\xf3\x01h\xb7\x10#\x7f\r\xf3\xa9\x94}4|\x00\xfe\x80'\xd76\x93\x9dx)\xa0\xcbrY\xb8\xcf\xa2|t\xcc\xfa\xd2u\x1e\xa3\x90\xf7`==\x1b\xa0Z\xbcQ\xf1J\xf2|0]\x0b\xbb\x9c\xce\x171\x1e<4E\x9b\xd9\x87\xf1m\r\xfe\xc1e!\xa6\x1f\x0f\xf1\x96S\xfc8\xe2d.r6\x81\x93\xdeX\xb6\xa3\x86D\x88\xf9\xf2\xd1\x83Z\xbf\"Q\xd1\xf0i\x82\x86\xa9M\xb8\xccg\x91i\xefC\x84U\xcf\xcd\x9b!WVF\xb0\x14\x05E\xaa\x18\x93\"\xc0\xc1\xd2V!t\xe2\xf9\xcd\xfba\xa0\xbc\x15\x14\x84\x9esfK\xbfC\xa2\xedJspo+\x81\x18(\x00\xf6+\x18\xedQ\xe6\xebW^\xf8\x80=\x10\xfb\xd6.'A\x979;)\x06\xf0\x85w\x95S\xd9\x1c9\xcc3k\x03\xf2w\x17\x97\xcc\nN0;0\x1f0\x07\x06\x05+\x0e\x03\x02\x1a\x04\x14\xb1\x82\x1d\xb1\xc8_\xbc\xf1^/\x01\xf7\xc1\x99\x95\xef\xf1<m\xe0\x04\x14\xe0\xef\xcd_\x83#\xc5*\x1dlN\xc0\xa4\xd0\x0c\"\xfa\xedDL\x02\x02\x07\xd0"
    CERT_CONTENT_NOT_PASSWORD_ENCODED = b'0\x82\n4\x02\x01\x030\x82\t\xf4\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\t\xe5\x04\x82\t\xe10\x82\t\xdd0\x82\x06\x16\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\x06\x07\x04\x82\x06\x030\x82\x05\xff0\x82\x05\xfb\x06\x0b*\x86H\x86\xf7\r\x01\x0c\n\x01\x02\xa0\x82\x04\xfe0\x82\x04\xfa0\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x030\x0e\x04\x08\x1f\xa53\xd3\x19\xe7Ac\x02\x02\x07\xd0\x04\x82\x04\xd8\xe9\xa4\x9e\xb6\x06+\x85\x82Pu\xd2\xb1\xa5\xbc\\\x9dq\xd8\xbb}\x02C\xe8\xf1Q\x01r\xf3{,\x92\x04\xe9\xab\x97AM\x0b\xd7R_\r7\xaf)~\xe3\xf8\x8d\xa4\xdc\xc1\xa3\x12\xa0\n\x19i\x08w\x9b\x0c\xd0\x8e\x01\xf7\xfa\xb9\x0c\x1d@R\x96_\x92H=\x82\x9b\xdb\xaf\xe5\xd0fn\xda\x82$\xc8f\nf\x96>A\xf4\x0c\xa1\xde\xd3rj\x85\xbc\xdcW3c\x9d\x137\x17\x80\x01\xb2f\xccFf\x14\xbd\xf9\xbe\xbf\xe1\x9eF\xe7\xaeq\xde\x8c\xa9\x94\x89I2\xb4\xacY\xb4\xd1\x02?\xce\xe0\xf9\x9d\xe7\x8a\xf0\xf1\x8d\xc0\xd5\x8d\x91\xe9P\xcd\xe9\xd4X\x00\xaa\xcdI\t-\xede\xcbT?\xfd\x8b\xa1\xaci0sw(\x1b\xb1\x833\x9fi\x82:9\xb4/ H\x07b\xd3\xf5-\xcbS`\x82\x10\x0b\xd1\x8f\xb8I\xce/\x14\xa20i\xa7\xef\xb8=\xe2Z\x15?z\xa9\x1b\xc2k\x0et\xf1\x18\x16\x07\xd8\x9a\xfd\xea\xe9\xb2Fq\x96\x04r\xcb\x16\xb3v\xfd\xac\xb5*\x07s1\x97\xc9\xe1\xf9I\x18\xe2\xf0{\xce\xa6\xba/\xcd\xf8?\xd2*\x8c\xb3f\xe8\x99h\xa8\x13\x03\xafs,\xa5A\xb3b\x9c#\xb7\xa1\x1b2w\xcd`\xd2\x95\r\xcd\x86\x8aq\xfb?\xfaO\xbe\x9d\xe9B\x9e\x80\xa1\xc2\xb5\\\xad\xf8\xf4i\n\xc8\x80j\x8c\x1a\xe2\x0be\xb1F\xb3{Kj\xed\t\xb9\xb3\xf2\x15\xf9\xd3E<7\xe1\xfb\x8d\x88\xc7\x9c\x81#l\x19\x07\xa5\x05\xdd\xdb\xf8\xc3\x1c\xff\xa7\x94\x9c\xc8]t~\x8e$/q\x10`g\xc1\xa1Q\xea|s\xd7\xaa\x9f\x0f\x9c#Og\x13\x95\xda}\x00\xc4\xf1\xc0S\xb8q\x9a\xddT\xffUY~\x07\x81\xc3]Qc\xe6\x7f\r\xd3bd\x0cG. e\xb2\xae\x80>,C\x81\xad\x83\xe4\xb5\x1f\x8c\xec\x8a$\xe3\x0c\xf2r\xa9\xed\xaf[[\xddL\xdd\x16\xf7\x1d&\x7f\xd8C\x0f\xc72\xcb\xd3J\xb4\x8a\xb9\n(\x86\x95B\xf4\xcd\x1b\xd5\xe4\xab\xb2G\xf1\xce!\x07@\xf0-\x1d\xbf\xcbD\xd3\x89\x07\\%\xe7\xce\x1d\x16z\xa4a\xf2\xedS\xcej\xd9uC]\x84\xa2\x801\xce\xf71\x14-\xc1\r}\xc8\xc6\x03W\xd4$\x9e\xe8QO\xec\xb3\x9e\x83\xa6\x90tu\x15X]\xb8!\x7f\xcaQ&bu\xb0!^\xcd\x99P\xbe\xe46J]\xa1\xa3\x8c\xcd\xc8\xca\xf8\xec\n\xc8\x8c\xc0\xd2\xd2$8\x95\x9d\x81\xdb\x9e\x05\x8f\x84\xaa\xfa\x07ci\xd5\xcb4\x1c\x9b\t\xe6\x02`M\xe1\x8e%P+.BI8\xcd\x94WT\x14~B5\x8fy\xafu\xdd\x10\x8dj"_\x9f\xd8\x84\xc3\xb9\xcb\x19m\x7f\xef`\x11\x06B\xd6g\xea\xe1\xc2\xc3\x19@\x0f\xd59\xf0\x01D\xfe\x08\x9ep~pE\xb1\x81\xd4\x7f\x9f>?_\xb2C\xfc%\x98\xfe,c!\x9c\x96\xaeH\xcc\x1cic(\xe6\x80)\x90W\x07\xfaOmQ:v\x87H[\xaa?\xf4Y\x89\xbaz\x96B\x96\xfbZ\x98\xf9Q\xfe\xe8\x1a\xf8.n\xca*\xc3`\xaa\x91}\xa4\xe7\x87\xf7\xff\xf4^\xf8\x01:r\xc8(\xa8\xfdf|WY[\xa7\xf4w\xfa@\xbc\\^w\xa8\xeb\x82\xe35G\xf7\x06f\xe34\x9aA\xbc\x1e\x88\xa84\xd2]\x95\x9d\xa6%T\xbb\x0bt\x93I\xc0+7\xa31\xa3?9\xb0B>\xd6J\ttT\x8f\xf8\x19\xec`\xab\xc0\xab\xab\x93G;UN)\x1b|\x0b\xde\x1d{\xffPLz\x08\xe4-f\\\xf1\xafM\xb7\x9e$:\xd8\xd2;\xfe\xc1\x02c\xa3\x16\x9c\xc5\x9b\xcdt\xb7\x99!\x02\xddL\xd62\xb9\xe7\xb4\x181\xe1S\xedJ\x83\x0b[\xc0B@\x93\x15\xcf\xb0\xaaS\xdd\xbfp{\x1cW0\xd2\x9d\x8aO\xaa\n\xba\x0e\xecm\x92\xdd\x84\x84\nlN\xd8\xe2n\xc7^\x85\x9c\xca\x0e\x05K\x8f\xb41\x9d\x07A\x812\xd4\xb4\'\x16:\xedG\x9d\xbfY\xd3\x05\xef\xd5hq\xaf\x88\xde\x068)\xca\x8b\xd4\x10pE\xc8e\x04i<\x18^\x1b\x7f\xfdJaP\x1f\xd4R\x10\xc5\xae\xe6Q\x08\x8b\xbcy*\x15\xb8\xb7G\xc1R\\\t\xbb\x93g\x9f\x1e\xdb7j\x02h\xe5\\@\xf0A\xfc^\x84U \xc9\xa7\x92%W\x0ep\x03\xb95gH!N\xfcjG\xb4\xc72\x0eq\x10W\xdd\xe8^Y\xa2p\xab\xd1\xcf\xe4\xd8q\xa9\xce]\xf9\xdbJ\x8e\xe9\xaaS\xed6y\x93~2\x8e\xbbx\x0eIF5\x16\xdco\xd1\xec;\tqm \xd3\x80\x93\xcc\xb38\xe9\x12\x1a\xb1\xbd\x1f\xb5\x80\xef\x8bR@f\'QF\xac\xd1\x1e\x18\x1e-\x80\x85\x82\xe8\x9f\xb6|E\xc1c\xe4\xcc\xd0\x96\x88\xc5\xa0\x83"\xa3\xa69\xfb\x10\xc2XN\x1e9\xe9\xeeB\x01\x00\xe8w\xc3\xb1\xb6\x9e\xbd\x8d\n\x92\x94Vc\x85mjA=\x92?\x12\x17\xa2nJV$\xcd\xea/XO\x00\xf9\x8b\xdc\xf0\xcef\xc8\x06\x94*M\xce\xfb\x0b\xe5/SC\xad\xed\xdfu\x95\x83S\xdc\xa9\xad:\xdc\t\xc8r\x9c\x1f\x16\x85\x0e\x11\xff\xa4\xeeJI\xddK\xf4!e\x9c\xb61\x81\xe90\x13\x06\t*\x86H\x86\xf7\r\x01\t\x151\x06\x04\x04\x01\x00\x00\x000W\x06\t*\x86H\x86\xf7\r\x01\t\x141J\x1eH\x00b\x00d\x008\x003\x007\x009\x00c\x001\x00-\x00a\x006\x005\x00c\x00-\x004\x003\x00e\x00e\x00-\x008\x001\x000\x00a\x00-\x005\x00a\x002\x004\x003\x004\x006\x003\x00f\x00c\x00e\x00c0y\x06\t+\x06\x01\x04\x01\x827\x11\x011l\x1ej\x00M\x00i\x00c\x00r\x00o\x00s\x00o\x00f\x00t\x00 \x00E\x00n\x00h\x00a\x00n\x00c\x00e\x00d\x00 \x00R\x00S\x00A\x00 \x00a\x00n\x00d\x00 \x00A\x00E\x00S\x00 \x00C\x00r\x00y\x00p\x00t\x00o\x00g\x00r\x00a\x00p\x00h\x00i\x00c\x00 \x00P\x00r\x00o\x00v\x00i\x00d\x00e\x00r0\x82\x03\xbf\x06\t*\x86H\x86\xf7\r\x01\x07\x06\xa0\x82\x03\xb00\x82\x03\xac\x02\x01\x000\x82\x03\xa5\x06\t*\x86H\x86\xf7\r\x01\x07\x010\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x060\x0e\x04\x08\xd0~p\xe13w{_\x02\x02\x07\xd0\x80\x82\x03x\x1e]uF\xa8\xb8\xdf\xf4\xb0x4\xf4\xe3r\xea\xee\xc7\x83k;\x07.\xde!W\x98b\x0f]\x87v\x06^\xe2\xc4Z\xd9\x16\xee\xe4z\xb5\xa5^R\xf8!V\x01\xcb\x90\xbf\x05\xdfWN\x8c\xe2\x059\xba\x02\xa0\xf3\xb0d\x0f\x94 |\xe89\x07\xa8\xff\x86\xc5\x12\x8c\xb0Pa\xaa\xb2\xb3\xbe\xe7\xd5 \xc7\xf6\xa5\xa0\xe9\x87\x93\x16\xea\xebPV\xc9\xda\x97B\x1e\xa1M)\x1c^\xe7\xfb\xbe\x00q;\x8e\xf4\r\xf3q\x87\xb9)g\xc8\xa1\x07i\x06\xca\xc8\x97S\xd3\xd3ihO\xaf(\xd7\xa0\t\xefo\x10\xb8\xeaE\xfc\xdf\x18\xf0\xd4\xe5\xbc\xbc\x12\x11\xc2p\xb4\xfd\xf8\x1b\x0e\xa8\xa9.N[?\xd2\xf3<rS\xe8\x96\xbeT\xc0\x91\x13\xc1\xa7\xc6#\xd9\x8f\xd3\xb0\x10d\xcb\x7f\x17\xd0\xe8\x8b\x1b\x9e\xee\t\xacl\x08cE\xc5\xaa\xae\xcc\xfd\x02\\\xa2\xc6\x19\xc5_V}o7\x92\xb5\xacY\xad\xabL\xb1\xeb}\xb3\xf6X\x99\xff?\xec\xd2\xd1\xcb~C\xcd\x00\xcbuu\xc0K\x10\xe5\xa2\x9f\x86\xa7D\xc2\xc6\x89\x8d\xdd\xa6\x87\xed\xb6dz\xec\xab\x8e\xa6\x98\xa8nR\xc3\x07`\xb1?\xfd\xe2yi\xc5_\x9c\x80\xa4\xfe\x18\x10\xd5{-u\x9a\xe3\x87\xc19\xb5\xdc\x82\x8c\x83\xd7\xc7G\xd2\x1e\xa8m\x12\xc8\x9a2O\xe4"\xd9\xa6\x1b;\xdd\x95\xe3a\x07\xc9\xe9\x1e\'\xfax\xab@s\x98\x8e\x8a\xd3U.\x95W\xd4S0`\x0f\xecF\x0f\xe4\x86]\xa6\x17\x03~sz\x1b\xd2\xaf\x9f\xf8$\x8d\x11\x0c\x92\x83ay\xbch\xabY\xb5\xa7Gl\xd3\x82\x88\x94\xbe\n\xa5XK\xd2\xc2\x9c\xda\xa1;@.\xdb\x86\x1d\x18\xe7}0\xb2\xf9\xcb\x0c\x8a\xee\x04&O\x06M\xc4\xd1\x8eV9\x84U\xf1DTdF\x131\xc3\x96\x07A\x17\x1f_\x89$\t\xa2!\xed\x85,E\xa7[\xcf\x0fv\n2\x99\x9e\xae2\x1b*\xcb\xab\xb1\tE\xd2\xb8~\xf5\xb5\xdc\x8b\x91\xf2\xe1\xe7\xe3\xfdA\x1a"\x82\xc5<#8\xf6v\xce]\x8fR0b\t\xdf%a\xe1-\xab\x1b \'&`\xe0\x80\xcc\xdef\x0e\xbe_\xcd\x86{P?\x116\xfe\xfc\x1b\xceK=b\xbdau2\x90 \xbaxHM\x89\xa4i\x11\xc2\x056\xc8\xfc\xa6\x95u\xe6\x14\x07\x02\xae\xad\xb2Q#\xde\x93s\xcfLc|1\xe6\xfb\x10C\x1d1(0N\x0c\xaav\xd1?\xf8j;\xc5+\x0b\xf3\x8e>\x0f\xda\x1cp\x99\x86\xbe\xc3\xa8t\\\xa4\x88?\x90\xb3\xa3qvh\xa5\x06\xf1a\xb6%\x18\x8eqc2\x04\xc7\xc0>i\xdc\x8fI\xbc\xb0\x82\xdc\x87j\xd9\xff\x05e{\xd2\x01\x0e\xf0\x91\x7f\xcb\xf8\xa27\xfb\xd1\x9c\x96\xadS\x97\x17\xb0\xf3F\xb4\xc6\xc3(/\xc4\x88\xdf\xf3M@n\xc4\xd88\xd0%hq\x0c\xae\xab\xbf\x91\xe6\xff\xd4np\xed\x9a\xab\x04\x83^/!\xf7\xf5\x91\xa54\xc9n\xb14\xb6\x8d\xdbQB-\x04\xf8\x98H\x98\xe10Ksw\xac\x0cc@\x92\x10\x1cA\x96\xb39gljl6\xd4cz\xd8it\x1e\xedZ]\xfa\x0c\x93\xce\x97\xcd"\x93e\xf8\xb1\x02b\xb9 \xb5\xc5W\x12\xf5\xe7\x81s\xf9$+\xf4\xee\x13\xdeQ\x02Cq\x15x\xe3\xd8\xbe&\xa4,k0U\xa9\x87\x15\xc7\x86\x82\xb0@Q\xfb\xbb\xf6\xa11\xbf\x1d[,\xec\x16`\xc5\xc2\x0f/\n\x8f\x9f\xebf\xfa\xf3\xcfW\x9d\xedD\xf4\xdf\x8c\x88\xc3{\x89s\xf6\xb20+\xa2J\xffx\xbd\xad\x9a9/\xee\xc2x?\xce\xc2{\xb8\x1b)\x0e\x8ao\xe3\x86{%n.~\x8c\x95\xc9\x85[\xfa\x1a070\x1f0\x07\x06\x05+\x0e\x03\x02\x1a\x04\x14\xc2\xeb\x94\x0bl\xc6q36\x8c\x8b\xfb\x87\xa2N\x0e\xa4\x00\x11.\x04\x14R)\xd7xhz=l\x84,\xcc\x07\xa6\xef\xd7i\xb0\xe9\x13o'

    def __init__(self, *args, **kwargs):
        super(CertificateClientTests, self).__init__(
            *args, replay_processors=[RetryAfterReplacer(), RequestUrlNormalizer()], **kwargs
        )

    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(CertificateClientTests, self).tearDown()

    def create_client(self, vault_uri, **kwargs):
        credential = self.get_credential(CertificateClient)
        return self.create_client_from_credential(
            CertificateClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    def _import_common_certificate(self, client, cert_name):
        cert_password = "123"
        cert_policy = CertificatePolicy(
            issuer_name="Self",
            subject="CN=DefaultPolicy",
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type="application/x-pkcs12",
            validity_in_months=12,
            key_usage=["digitalSignature", "keyEncipherment"],
        )
        return client.import_certificate(
            certificate_name=cert_name, certificate_bytes=CertificateClientTests.CERT_CONTENT_PASSWORD_ENODED, policy=cert_policy, password=cert_password
        )

    def _validate_certificate_operation(self, pending_cert_operation, vault, cert_name, original_cert_policy):
        self.assertIsNotNone(pending_cert_operation)
        self.assertIsNotNone(pending_cert_operation.csr)
        self.assertEqual(original_cert_policy.issuer_name, pending_cert_operation.issuer_name)
        pending_id = parse_key_vault_certificate_id(pending_cert_operation.id)
        self.assertEqual(pending_id.vault_url.strip("/"), vault.strip("/"))
        self.assertEqual(pending_id.name, cert_name)

    def _validate_certificate_bundle(self, cert, cert_name, cert_policy):
        self.assertIsNotNone(cert)
        self.assertEqual(cert_name, cert.name)
        self.assertIsNotNone(cert.cer)
        self.assertIsNotNone(cert.policy)
        self._validate_certificate_policy(cert_policy, cert_policy)

    def _validate_certificate_policy(self, a, b):
        self.assertEqual(a.issuer_name, b.issuer_name)
        self.assertEqual(a.subject, b.subject)
        self.assertEqual(a.exportable, b.exportable)
        self.assertEqual(a.key_type, b.key_type)
        self.assertEqual(a.key_size, b.key_size)
        self.assertEqual(a.reuse_key, b.reuse_key)
        self.assertEqual(a.key_curve_name, b.key_curve_name)
        if a.enhanced_key_usage:
            self.assertEqual(set(a.enhanced_key_usage), set(b.enhanced_key_usage))
        if a.key_usage:
            self.assertEqual(set(a.key_usage), set(b.key_usage))
        self.assertEqual(a.content_type, b.content_type)
        self.assertEqual(a.validity_in_months, b.validity_in_months)
        self.assertEqual(a.certificate_type, b.certificate_type)
        self.assertEqual(a.certificate_transparency, b.certificate_transparency)
        self._validate_sans(a, b)
        if a.lifetime_actions:
            self._validate_lifetime_actions(a.lifetime_actions, b.lifetime_actions)

    def _validate_sans(self, a, b):
        if a.san_dns_names:
            self.assertEqual(set(a.san_dns_names), set(b.san_dns_names))
        if a.san_emails:
            self.assertEqual(set(a.san_emails), set(b.san_emails))
        if a.san_user_principal_names:
            self.assertEqual(set(a.san_user_principal_names), set(b.san_user_principal_names))

    def _validate_lifetime_actions(self, a, b):
        self.assertEqual(len(a), len(b))
        for a_entry in a:
            b_entry = next(x for x in b if x.action == a_entry.action)
            self.assertEqual(a_entry.lifetime_percentage, b_entry.lifetime_percentage)
            self.assertEqual(a_entry.days_before_expiry, b_entry.days_before_expiry)

    def _validate_certificate_list(self, a, b):
        # verify that all certificates in a exist in b
        for cert in b:
            if cert.id in a.keys():
                del a[cert.id]
        self.assertEqual(len(a), 0)

    def _validate_certificate_contacts(self, a, b):
        self.assertEqual(len(a), len(b))
        for a_entry in a:
            b_entry = next(x for x in b if x.email == a_entry.email)
            self.assertEqual(a_entry.name, b_entry.name)
            self.assertEqual(a_entry.phone, b_entry.phone)

    def _admin_contact_equal(self, a, b):
        return a.first_name == b.first_name and a.last_name == b.last_name and a.email == b.email and a.phone == b.phone

    def _validate_certificate_issuer(self, a, b):
        self.assertEqual(a.provider, b.provider)
        self.assertEqual(a.account_id, b.account_id)
        self.assertEqual(len(a.admin_contacts), len(b.admin_contacts))
        for a_admin_contact in a.admin_contacts:
            b_admin_contact = next(
                (ad for ad in b.admin_contacts if self._admin_contact_equal(a_admin_contact, ad)), None
            )
            self.assertIsNotNone(b_admin_contact)
        self.assertEqual(a.password, b.password)
        self.assertEqual(a.organization_id, b.organization_id)

    def _validate_certificate_issuer_properties(self, a, b):
        self.assertEqual(a.id, b.id)
        self.assertEqual(a.name, b.name)
        self.assertEqual(a.provider, b.provider)

    @KeyVaultPreparer()
    def test_crud_operations(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        cert_name = self.get_resource_name("cert")
        lifetime_actions = [LifetimeAction(lifetime_percentage=80, action=CertificatePolicyAction.auto_renew)]
        cert_policy = CertificatePolicy(
            issuer_name="Self",
            subject="CN=DefaultPolicy",
            exportable=True,
            key_type=KeyType.rsa,
            key_size=2048,
            reuse_key=False,
            content_type=CertificateContentType.pkcs12,
            lifetime_actions=lifetime_actions,
            validity_in_months=12,
            key_usage=[KeyUsageType.digital_signature, KeyUsageType.key_encipherment],
        )

        # create certificate
        certificate = client.begin_create_certificate(cert_name, CertificatePolicy.get_default()).result()

        self._validate_certificate_bundle(cert=certificate, cert_name=cert_name, cert_policy=cert_policy)

        self.assertEqual(client.get_certificate_operation(certificate_name=cert_name).status.lower(), "completed")

        # get certificate
        cert = client.get_certificate(certificate_name=cert_name)
        self._validate_certificate_bundle(cert=cert, cert_name=cert_name, cert_policy=cert_policy)

        # update certificate, ensuring the new updated_on value is at least one second later than the original
        if self.is_live:
            time.sleep(1)
        tags = {"tag1": "updated_value1"}
        updated_cert = client.update_certificate_properties(cert_name, tags=tags)
        self._validate_certificate_bundle(cert=updated_cert, cert_name=cert_name, cert_policy=cert_policy)
        self.assertEqual(tags, updated_cert.properties.tags)
        self.assertEqual(cert.id, updated_cert.id)
        self.assertNotEqual(cert.properties.updated_on, updated_cert.properties.updated_on)

        # delete certificate
        delete_cert_poller = client.begin_delete_certificate(cert_name)
        deleted_cert_bundle = delete_cert_poller.result()
        self._validate_certificate_bundle(cert=deleted_cert_bundle, cert_name=cert_name, cert_policy=cert_policy)
        delete_cert_poller.wait()

        # get certificate returns not found
        try:
            client.get_certificate_version(cert_name, deleted_cert_bundle.properties.version)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

    @KeyVaultPreparer()
    def test_import_certificate_not_password_encoded_no_policy(self, azure_keyvault_url):
        client = self.create_client(azure_keyvault_url)

        # If a certificate is not password encoded, we can import the certificate
        # without passing in 'password'
        certificate = client.import_certificate(
            certificate_name=self.get_resource_name("importNotPasswordEncodedCertificate"),
            certificate_bytes=CertificateClientTests.CERT_CONTENT_NOT_PASSWORD_ENCODED,
        )
        self.assertIsNotNone(certificate.policy)

    @KeyVaultPreparer()
    def test_import_certificate_password_encoded_no_policy(self, azure_keyvault_url):
        client = self.create_client(azure_keyvault_url)

        # If a certificate is password encoded, we have to pass in 'password'
        # when importing the certificate
        certificate = client.import_certificate(
            certificate_name=self.get_resource_name("importPasswordEncodedCertificate"),
            certificate_bytes=CertificateClientTests.CERT_CONTENT_PASSWORD_ENODED,
            password="123"
        )
        self.assertIsNotNone(certificate.policy)

    @KeyVaultPreparer()
    def test_list(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        max_certificates = self.list_test_size
        expected = {}

        # import some certificates
        for x in range(max_certificates):
            cert_name = self.get_resource_name("cert{}".format(x))
            error_count = 0
            try:
                cert_bundle = self._import_common_certificate(client=client, cert_name=cert_name)
                # Going to remove the ID from the last '/' onwards. This is because list_properties_of_certificates
                # doesn't return the version in the ID
                cid = "/".join(cert_bundle.id.split("/")[:-1])
                expected[cid] = cert_bundle
            except Exception as ex:
                if hasattr(ex, "message") and "Throttled" in ex.message:
                    error_count += 1
                    time.sleep(2.5 * error_count)
                    continue
                else:
                    raise ex

        # list certificates
        returned_certificates = client.list_properties_of_certificates(max_page_size=max_certificates - 1)
        self._validate_certificate_list(expected, returned_certificates)

    @KeyVaultPreparer()
    def test_list_certificate_versions(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        cert_name = self.get_resource_name("certver")

        max_certificates = self.list_test_size
        expected = {}

        # import same certificates as different versions
        for x in range(max_certificates):
            error_count = 0
            try:
                cert_bundle = self._import_common_certificate(client=client, cert_name=cert_name)
                expected[cert_bundle.id] = cert_bundle
            except Exception as ex:
                if hasattr(ex, "message") and "Throttled" in ex.message:
                    error_count += 1
                    time.sleep(2.5 * error_count)
                    continue
                else:
                    raise ex

        # list certificate versions
        self._validate_certificate_list(
            expected,
            client.list_properties_of_certificate_versions(
                certificate_name=cert_name, max_page_size=max_certificates - 1
            ),
        )

    @KeyVaultPreparer()
    def test_crud_contacts(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        contact_list = [
            CertificateContact(email="admin@contoso.com", name="John Doe", phone="1111111111"),
            CertificateContact(email="admin2@contoso.com", name="John Doe2", phone="2222222222"),
        ]

        # create certificate contacts
        contacts = client.set_contacts(contacts=contact_list)
        self._validate_certificate_contacts(contact_list, contacts)

        # get certificate contacts
        contacts = client.get_contacts()
        self._validate_certificate_contacts(contact_list, contacts)

        # delete certificate contacts
        contacts = client.delete_contacts()
        self._validate_certificate_contacts(contact_list, contacts)

        # get certificate contacts returns not found
        try:
            client.get_contacts()
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

    @KeyVaultPreparer()
    def test_recover_and_purge(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        certs = {}
        # create certificates to recover
        for i in range(self.list_test_size):
            cert_name = self.get_resource_name("certrec{}".format(str(i)))
            certs[cert_name] = self._import_common_certificate(client=client, cert_name=cert_name)

        # create certificates to purge
        for i in range(self.list_test_size):
            cert_name = self.get_resource_name("certprg{}".format(str(i)))
            certs[cert_name] = self._import_common_certificate(client=client, cert_name=cert_name)

        # delete all certificates
        for cert_name in certs.keys():
            client.begin_delete_certificate(certificate_name=cert_name).wait()

        # validate all our deleted certificates are returned by list_deleted_certificates
        deleted = [parse_key_vault_certificate_id(source_id=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(all(c in deleted for c in certs.keys()))

        # recover select certificates (test resources have a "livekvtest" prefix)
        for certificate_name in [c for c in certs.keys() if c.startswith("livekvtestcertrec")]:
            client.begin_recover_deleted_certificate(certificate_name=certificate_name).wait()

        # purge select certificates
        for certificate_name in [c for c in certs.keys() if c.startswith("livekvtestcertprg")]:
            client.purge_deleted_certificate(certificate_name)

        if not self.is_playback():
            time.sleep(50)

        # validate none of our deleted certificates are returned by list_deleted_certificates
        deleted = [parse_key_vault_certificate_id(source_id=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(not any(c in deleted for c in certs.keys()))

        # validate the recovered certificates
        expected = {k: v for k, v in certs.items() if k.startswith("livekvtestcertrec")}
        actual = {k: client.get_certificate_version(certificate_name=k, version="") for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))

    @KeyVaultPreparer()
    def test_async_request_cancellation_and_deletion(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        cert_name = self.get_resource_name("asyncCanceledDeletedCert")
        cert_policy = CertificatePolicy.get_default()
        # create certificate
        create_certificate_poller = client.begin_create_certificate(certificate_name=cert_name, policy=cert_policy)

        # cancel certificate operation
        cancel_operation = client.cancel_certificate_operation(certificate_name=cert_name)
        self.assertTrue(hasattr(cancel_operation, "cancellation_requested"))
        self.assertTrue(cancel_operation.cancellation_requested)
        self._validate_certificate_operation(
            pending_cert_operation=cancel_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            original_cert_policy=cert_policy,
        )

        self.assertEqual(create_certificate_poller.result().status.lower(), "cancelled")

        retrieved_operation = client.get_certificate_operation(cert_name)
        self.assertTrue(hasattr(retrieved_operation, "cancellation_requested"))
        self.assertTrue(retrieved_operation.cancellation_requested)
        self._validate_certificate_operation(
            pending_cert_operation=retrieved_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            original_cert_policy=cert_policy,
        )

        # delete certificate operation
        deleted_operation = client.delete_certificate_operation(certificate_name=cert_name)
        self.assertIsNotNone(deleted_operation)
        self._validate_certificate_operation(
            pending_cert_operation=deleted_operation,
            vault=client.vault_url,
            cert_name=cert_name,
            original_cert_policy=cert_policy,
        )

        try:
            client.get_certificate_operation(certificate_name=cert_name)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

        # delete cancelled certificate
        client.begin_delete_certificate(cert_name).wait()

    @KeyVaultPreparer()
    def test_policy(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        cert_name = self.get_resource_name("policyCertificate")
        cert_policy = CertificatePolicy(
            issuer_name="Self",
            subject="CN=DefaultPolicy",
            exportable=True,
            key_type=KeyType.rsa,
            key_size=2048,
            reuse_key=True,
            enhanced_key_usage=["1.3.6.1.5.5.7.3.1", "1.3.6.1.5.5.7.3.2"],
            key_usage=[KeyUsageType.decipher_only],
            content_type=CertificateContentType.pkcs12,
            validity_in_months=12,
            lifetime_actions=[LifetimeAction(action=CertificatePolicyAction.email_contacts, lifetime_percentage=98)],
            certificate_transparency=False,
            san_dns_names=["sdk.azure-int.net"],
        )

        # get certificate policy
        client.begin_create_certificate(certificate_name=cert_name, policy=cert_policy).wait()

        returned_policy = client.get_certificate_policy(cert_name)

        self._validate_certificate_policy(cert_policy, returned_policy)

        cert_policy._key_type = KeyType.ec
        cert_policy._key_size = 256
        cert_policy._key_curve_name = KeyCurveName.p_256

        returned_policy = client.update_certificate_policy(certificate_name=cert_name, policy=cert_policy)

        self._validate_certificate_policy(cert_policy, returned_policy)

    @KeyVaultPreparer()
    def test_get_pending_certificate_signing_request(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        cert_name = self.get_resource_name("unknownIssuerCert")

        # get pending certificate signing request
        certificate = client.begin_create_certificate(
            certificate_name=cert_name, policy=CertificatePolicy.get_default()
        ).wait()
        pending_version_csr = client.get_certificate_operation(certificate_name=cert_name).csr
        self.assertEqual(client.get_certificate_operation(certificate_name=cert_name).csr, pending_version_csr)

    @KeyVaultPreparer()
    def test_backup_restore(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        policy = CertificatePolicy.get_default()
        policy._san_user_principal_names = ["john.doe@domain.com"]
        cert_name = self.get_resource_name("cert")
        # create certificate
        create_certificate_poller = client.begin_create_certificate(certificate_name=cert_name, policy=policy)
        create_certificate_poller.wait()

        # create a backup
        certificate_backup = client.backup_certificate(certificate_name=cert_name)

        # delete the certificate
        client.begin_delete_certificate(certificate_name=cert_name).wait()

        # purge the certificate
        client.purge_deleted_certificate(certificate_name=cert_name)

        # restore certificate
        restore_function = functools.partial(client.restore_certificate_backup, certificate_backup)
        restored_certificate = self._poll_until_no_exception(restore_function, ResourceExistsError)
        self._validate_certificate_bundle(cert=restored_certificate, cert_name=cert_name, cert_policy=policy)

    @KeyVaultPreparer()
    def test_crud_issuer(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        issuer_name = self.get_resource_name("issuer")
        admin_contacts = [
            AdministratorContact(first_name="John", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
        ]

        # create certificate issuer
        issuer = client.create_issuer(
            issuer_name, "Test", account_id="keyvaultuser", admin_contacts=admin_contacts, enabled=True
        )

        expected = CertificateIssuer(
            provider="Test",
            account_id="keyvaultuser",
            admin_contacts=admin_contacts,
            issuer_id=client.vault_url + "/certificates/issuers/" + issuer_name,
        )

        self._validate_certificate_issuer(expected, issuer)

        # get certificate issuer
        issuer = client.get_issuer(issuer_name)
        self._validate_certificate_issuer(expected, issuer)

        # list certificate issuers
        issuer2_name = self.get_resource_name("issuer2")

        client.create_issuer(
            issuer_name=issuer2_name,
            provider="Test",
            account_id="keyvaultuser2",
            admin_contacts=admin_contacts,
            enabled=True,
        )

        expected_base_1 = IssuerProperties(
            issuer_id=client.vault_url + "/certificates/issuers/" + issuer_name, provider="Test"
        )

        expected_base_2 = IssuerProperties(
            issuer_id=client.vault_url + "/certificates/issuers/" + issuer2_name, provider="Test"
        )
        expected_issuers = [expected_base_1, expected_base_2]

        issuers = list(client.list_properties_of_issuers())
        for issuer in issuers:
            exp_issuer = next((i for i in expected_issuers if i.name == issuer.name), None)
            if exp_issuer:
                self._validate_certificate_issuer_properties(exp_issuer, issuer)
                expected_issuers.remove(exp_issuer)
        self.assertEqual(len(expected_issuers), 0)

        # update certificate issuer
        admin_contacts = [
            AdministratorContact(first_name="Jane", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
        ]

        expected = CertificateIssuer(
            provider="Test",
            account_id="keyvaultuser",
            admin_contacts=admin_contacts,
            issuer_id=client.vault_url + "/certificates/issuers/" + issuer_name,
        )
        issuer = client.update_issuer(issuer_name=issuer_name, admin_contacts=admin_contacts)
        self._validate_certificate_issuer(expected, issuer)

        # delete certificate issuer
        client.delete_issuer(issuer_name=issuer_name)

        # get certificate issuer returns not found
        try:
            client.get_issuer(issuer_name=issuer_name)
            self.fail("Get should fail")
        except Exception as ex:
            if not hasattr(ex, "message") or "not found" not in ex.message.lower():
                raise ex

    @KeyVaultPreparer()
    def test_logging_enabled(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, logging_enable=True)

        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        issuer_name = self.get_resource_name("issuer")
        client.create_issuer(issuer_name=issuer_name, provider="Test")

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                try:
                    body = json.loads(message.message)
                    if body["provider"] == "Test":
                        return
                except (ValueError, KeyError):
                    # this means the message is not JSON or has no kty property
                    pass

        assert False, "Expected request body wasn't logged"

    @KeyVaultPreparer()
    def test_logging_disabled(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, logging_enable=False)

        mock_handler = MockHandler()

        logger = logging.getLogger("azure")
        logger.addHandler(mock_handler)
        logger.setLevel(logging.DEBUG)

        issuer_name = self.get_resource_name("issuer")
        client.create_issuer(issuer_name=issuer_name, provider="Test")

        for message in mock_handler.messages:
            if message.levelname == "DEBUG" and message.funcName == "on_request":
                try:
                    body = json.loads(message.message)
                    assert body["provider"] != "Test", "Client request body was logged"
                except (ValueError, KeyError):
                    # this means the message is not JSON or has no kty property
                    pass

    @KeyVaultPreparer()
    def test_2016_10_01_models(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, api_version=ApiVersion.V2016_10_01)

        """The client should correctly deserialize version 2016-10-01 models"""

        cert_name = self.get_resource_name("cert")
        cert = client.begin_create_certificate(cert_name, CertificatePolicy.get_default()).result()

        # these properties don't exist in version 2016-10-01
        assert cert.policy.key_curve_name is None
        assert cert.policy.certificate_transparency is None

    @KeyVaultPreparer()
    def test_get_certificate_version(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url)

        cert_name = self.get_resource_name("cert")
        for _ in range(self.list_test_size):
            client.begin_create_certificate(cert_name, CertificatePolicy.get_default()).wait()

        for version_properties in client.list_properties_of_certificate_versions(cert_name):
            cert = client.get_certificate_version(version_properties.name, version_properties.version)

            # This isn't factored out into a helper method because the properties are not exactly equal.
            # get_certificate_version sets "recovery_days" and "recovery_level" but the list method does not.
            # (This is Key Vault's behavior, not an SDK limitation.)
            assert version_properties.created_on == cert.properties.created_on
            assert version_properties.enabled == cert.properties.enabled
            assert version_properties.expires_on == cert.properties.expires_on
            assert version_properties.id == cert.properties.id
            assert version_properties.name == cert.properties.name
            assert version_properties.not_before == cert.properties.not_before
            assert version_properties.tags == cert.properties.tags
            assert version_properties.updated_on == cert.properties.updated_on
            assert version_properties.vault_url == cert.properties.vault_url
            assert version_properties.version == cert.properties.version
            assert version_properties.x509_thumbprint == cert.properties.x509_thumbprint

    @KeyVaultPreparer()
    def test_list_properties_of_certificates_2016_10_01(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, api_version=ApiVersion.V2016_10_01)

        [_ for _ in client.list_properties_of_certificates()]

        with pytest.raises(NotImplementedError) as excinfo:
            [_ for _ in client.list_properties_of_certificates(include_pending=True)]

        assert "The 'include_pending' parameter to `list_properties_of_certificates` is only available for API versions v7.0 and up" in str(excinfo.value)

    @KeyVaultPreparer()
    def test_list_deleted_certificates_2016_10_01(self, azure_keyvault_url, **kwargs):
        client = self.create_client(azure_keyvault_url, api_version=ApiVersion.V2016_10_01)


        [_ for _ in client.list_deleted_certificates()]

        with pytest.raises(NotImplementedError) as excinfo:
            [_ for _ in client.list_deleted_certificates(include_pending=True)]

        assert "The 'include_pending' parameter to `list_deleted_certificates` is only available for API versions v7.0 and up" in str(excinfo.value)


def test_service_headers_allowed_in_logs():
    service_headers = {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
    client = CertificateClient("...", object())
    assert service_headers.issubset(client._client._config.http_logging_policy.allowed_header_names)


def test_custom_hook_policy():
    class CustomHookPolicy(SansIOHTTPPolicy):
        pass

    client = CertificateClient("...", object(), custom_hook_policy=CustomHookPolicy())
    assert isinstance(client._client._config.custom_hook_policy, CustomHookPolicy)
