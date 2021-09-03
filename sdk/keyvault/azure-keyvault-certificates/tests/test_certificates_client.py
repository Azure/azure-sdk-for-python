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
    KeyVaultCertificateIdentifier,
    CertificateContentType,
    LifetimeAction,
    CertificateIssuer,
    IssuerProperties,
    WellKnownIssuerNames
)
from azure.keyvault.certificates._client import NO_SAN_OR_SUBJECT
import pytest

from _shared.test_case import KeyVaultTestCase
from _test_case import client_setup, get_decorator, CertificatesTestCase


all_api_versions = get_decorator()
logging_enabled = get_decorator(logging_enable=True)
logging_disabled = get_decorator(logging_enable=False)
exclude_2016_10_01 = get_decorator(api_versions=[v for v in ApiVersion if v != ApiVersion.V2016_10_01])
only_2016_10_01 = get_decorator(api_versions=[ApiVersion.V2016_10_01])


CERT_CONTENT_PASSWORD_ENCODED = b'0\x82\t\xb1\x02\x01\x030\x82\tw\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\th\x04\x82\td0\x82\t`0\x82\x04\x17\x06\t*\x86H\x86\xf7\r\x01\x07\x06\xa0\x82\x04\x080\x82\x04\x04\x02\x01\x000\x82\x03\xfd\x06\t*\x86H\x86\xf7\r\x01\x07\x010\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x060\x0e\x04\x08X\xb2\x8c\xa9\xed\x830\xd7\x02\x02\x08\x00\x80\x82\x03\xd0\xd7\xf2Au\xa4\x18\xcbL\x8c&\xbd\x07\x01\xb6C\xadse\xb6\xc6C \xa85\xee}\xc9<6uU\x9b\x03xK\xb8\xc6\x8e\xc6\xbb\x12\xfb\x96\x03\x89\x15a\xcb\xff5\xe5i\xecKnqG\x88\xee\xd9c}\xea?\x19\x17\xbd\x035\x87\xf2O_\x12-\x1aJ\xc5\xadf\xa4\xf15\x18\xa4Cb\x86\xb1\xf5,\xb8\xb3\'nX\x9c\x18\x19\xce\xbf\xfa\xb0g!\x1a y\xb1;|\xa9@\xe5\x90\x92\xb1\xe0vJD\x06\xf7|\xac\x9a\x11k\x86Jl\xe1K\xdaa\xb0\xb2GY^\xb9>\xdb9`\x1b^~\xd9\xb5\xebx\xe8\x9c\xf8X\xab\xa7\xe4\xdc\x8a!{V\xa6C\xbc\xb2\x0b2\xdbK\xaeBJ\x92\x8den8\xa6\xba\x9c$dg\x98\x98\xfeF\xf7\x02E\x91\xa8\xae\xec\x9c\x1b}\xf7\x806\xd6B\x86\xf1\xf6T\xeb\xbd\x03\xc3[7\xb6,m.Q6X<\x18\x9d\xbd\xdfP\xb2s\x9a\xd4\xd7bL\x9aDV\xd6\xa0RO\x1e\xb3\xcc\xbb\xd2\xbde\x04\xd8\xfde\xd3pT\xa3\xda\xa8\x10R]9I\x03\x81\x88\x9a;n}dU?\x97M:\xc2?\x93\x84,\xed/\xbd\xa2\x14W\xda&3\x0b\x9a\xf6\x85\x1e\x81h\x12\xd0i\x00\x0e\x1b\xdc\xee\r\x8f\x90\x9c9\xba\n\x16\xdbs\x05\xac\xb3\xd4\xec\x9bv0\xb5\xe7\x04]\xdd\x86\xee\xb1\x91\xfe\xcd0`\x9a\xd3}\xf4:}\xa8\x03.+\xbbx\xec"\xa2\xa4\xaf\x1c3\xdb\xab\x91\xac<\xf8g-\x86\xdeU\x1bp\xf6\x8f\xed>\xc8a\xdb\xb8\xe0O\xf5\xdf\xd7M\xc4vo\xa0k\x91\x16\xa5\x88I\xb8\xf9\x9eF9\xa5\xc4\x14\xae\x01\x99:\x93\x9e\xf7(&9\'\x94U\x8e\xdd \x9cE)n\xd7\xd4\xed\xcd\x97\x82\xe9\xa1\xa2\x96\xe3i\xd33\xbcn\xa1T8;\xf1\xa0j\x91\xea\xbe\x0c\x8a\x8e$\xb3/\xdc\xebE\x90\x17\x12\x9a\xca@\x04\x0c\t\xba\xdebk\xb3x\x9a\x17:\xe8*`Op\x1e\x91\'x\xf5\xa9+\xb1\xa9\x03\xed0\x00\x9d\xe0\xb2\xa1Dh\xb4\xba<\x05\x175\xaaW\xe5\xa7\xfdT\xfa\xd9zpA`U\x08\xc4\xf5\'\xe2\xe2s\xfa\x9d\x8f\x18\xc5\x80\xf7A\xf89{\xf8y9P\xdaZ\xaa\x12\xa0\xd8g\x93.\xc2\xd20\xb7\xab\xc7\xd4S\xbb\x87a\xaa\x88\xc6\xd57\xf7$M*d\x14\xa6\x94n\xc8\xaa\x11"\x9f\xcc>\xf5\xd9\x8c\x8d*k\n)M={g7I\xa8\x02\to3">\xe4\x82\xca\xda\r\xc2\xae\xbe\xa3\xaa\x8es\x12^\\h\xf8\xc8\rq\xa62Hp34<K\xf7\x85\xb2\xee\xc3\x88\x1a\x88\x19\x991\x03\x11WO\xbegYC\x94\xca\xb5\xa9\xf7c\x0b\xecS\x1ef\xb7\x15=\xb7[\x90")J\xec\xf2\x1b\x7fTkB)\xaa\xe9E\xe9BF\xadsZ\xf5\xb7\xe3`\xc3-\x99\x9e&s\xc1\xa9.U\xce\x03\x91j\xb4y\xa0\xc7\x8d\x1d\x92\xe5\xadVf\xd0\x1c\xf1B\x073\xf1\x105\xc5Yi\x07\xa3\x064{@\x99\x8fc\x97\x93\x82a>\xec\x86\xd01\xb9\xfc\xf2s]\x12R\xa2\xa6ijKw:\xc0\xee{/L\xd1J\xf6\xeb\x04,T\xb9R8\x077U}\x11.\xc6o\x8az\xfdih\x04\xb8\xe2\xb72\x81\x1c\xecDj\xfd\x80J\x1e{\xf2:V\x03[\x1a0\x95\xd3\xc1\xfcR!y+O\xd5l\xdfw\xf8KZy\xf3P\x05\xa54|R\xd9Q\xfdg\xc4\xc8-\x812J\xa9M\xa4\xbb\xf7zG\xcd\x81\xff\x82\xd6\x089\xef\\\x00U\t\x0f\xb5Z`y\x8du3\xc1\x80\x05Uq\xea\xa5\x96\xc6tN\xea+\xae\xb7\x19\x1b\xd3\xd0"\r\xd8\\%\x8d\x93\x13\xb5\x83W\t\x03\xbaN[\x1eT\xb5\xfc\n\xb2\xdd\xc4h\xa8&\x89|\xe4\xd5\xab\x8fv\x12\x0f\xff\xe0\x1bp\xec\xd1\x18\x87\xfbG\xd7r\xe3z\xee)\xf6D-\xd6)\xf6\x94\t\xc5\x13\xba\xbe\xf5M\xab\xb6\x7f~\xd2Y\x9fE\xaf3\x87B\xa2U\xa0\xff\xdd)1\xb5P\x9f0\x82\x05A\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\x052\x04\x82\x05.0\x82\x05*0\x82\x05&\x06\x0b*\x86H\x86\xf7\r\x01\x0c\n\x01\x02\xa0\x82\x04\xee0\x82\x04\xea0\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x030\x0e\x04\x08\x00\xc9N\x15u\x14D\xf1\x02\x02\x08\x00\x04\x82\x04\xc8V.\xb2P\x8f\xab+k\xd2m\xc0\xbc\x1aS$\xc9\xb7Rk\xfd\xe1x:\xcf\xe9a\x97\xaa\x10\xfc)_W\xb4\xc1iF\xf5\x82\xf35\xdb>\xfe\x85&\xee\xc9\x97\xc5\'\t\xbf\xac\xae\\\xdb\xc0GV\x96K\xe7;\xde\x86xQ\x00\xb8\xed\xeb\xbc\x88\x11XL\x9az\x9eJ\xffO!\x1e\xc5\xd6\xbc\xeb\x18\x11\x97\x95\xed\xe2\xd8\xc0\xb3\r\x00\xf7\xf9\x04C\xfem\xc7P_\xd6\x0f\xd2\xcb\xc7\xd44\xb9\xc5\x1fw>"\xd2\xad;!\xb4@\x0bP\xcf\xff\x19&\x03k\xaa\x8b\xfc\xd6X\x87^s}mv\xa6\xf2G\xbb@\xda\x152]zU\x1b\x96q\xc7!\xee\xc2Q\x05dG\x07\xa6\xc1\xe7\rN4\xe6(x\xe7\xe5\xa1p\x0f\x91\xec#:o\x0c\xcb\xb1\x17\xf5M\x9e\xcb\x8f\x1d\xc5\xc3\xce<\x1bD:\x93\x83\xaf:drZ\xd0\x80?\xfb($#\xef\xb8\xe5\xe7"\xf2W8\x93d\x0e\xdb\xf9\x17*\x10\x17\xecrk\xd8\x1fo\xa6\xbe\xb7\xf9\x1b\xc0qa3^-\xea\xbc\x82g\x9d\xb9\x7f\xce\x8f\x12,\xdc~(\xd3\x0e\xf7D\xd8MD\xa8VenpU\x08|\t\xf5\xe2nr4\xb1^j`\xb2V\xdd\xae\x83Gf\x93\r\x03\xe6\xc3f*\xa0r\x07\x0e\x1c\xf2\xbe1\xa1;(J"D\xa9\t\xed\x0e\x13\xddu\x9f\xac\xba\x83h\x0bE\x9a\x12\r\'\x0e\xc7\x99+\x9e\x96,\x8e\x10\xcfG\xbdQ\xda\xf0"\x80\xd4\x83<\xc5\xd1\x7f\x9e\xbb\x06\x11\x8a\xf0\xfce-=\xa1ueq\x01\xa1\xe1N\xd7!\xfe\xe8\x99\x13\xd9,\x86o7\xa2\xd8\xa0\x02J\x1a\xaef\x91j&\xf1\xfa\x81+qd\xfehh\xe4\xf4P\x816\x10\xac\xfd\xfbj^M\xa8D\xe5r\xf7/\xb5\xe6\xab\xf5*{;\x11(\xe0A\xb1\x1f\xaeM z\xc3\xc7V\x9b\x07\x9ajZ\x010\xbdbF\xc3I,1md\xf2o\x8b\xbc\xd62\xad1\x8dLh/{\xa50\x9f#?o\xee\xd6k\xa6\xd2\\\xa5;n\x88\x16\xa8;W\xbe8\x81+u\x14\xf1\xd1\xebl\xf0\x1bl\xd5\xd9\xbea\xbb_\xe16xWxOJ2\xc7p\xc1\xd7\xcbRG*^\xb3A\x06\xa9\x03\x8c]vK\x8a\xed\xecp\x9a\x02<u|O\xce\xfe\x83*\x0b\xc6\x04;t\xd8k\xb9\x8b\xe2f\xa3\xeeT}%\xad\'\xee\x05G\xa4\xa1\x88\xcb\xa2\x14z\xf6\x9d>\x1c\\\xbc\xcd\x7ft\xc6\xb1;\xf8]\xe3\x10\x83@-U\xf0\x16*\xc6\xcb\xfa@~\x1do\x13\xa3\xdd\x84\xee\xc4>\xe6ED\x88\xeen A\xb1\xb6\x8c9Ta5\x8ct&\x90\xa3\r\x91\x08\xf0D\xec\x95\xa4\xed\xe7\xef_\xf4p\x92t\x17\x8bn\x93pk\x15\x84\x06t\xff\x94\xdf\xdb\xe2\x8f\xd2\x93\x81g\x96>\xe2\xc4\x1cm H]4*M\x1e>\xa91&N\x8b\x12\x8f\x83\x93\x0c\xe3\xbam/\x9bVy\xach\xd0\t\xf4\xe5Z\xf5\xb3@]#\xa5\xfb\xa5\x8f\x123Q\xdf>6[\xf7\xdd\xfa\xc5$\xd1\x8d\x06S\x86\x1c6 H|\xc3\xe4\x91\t,Vj\x94\xdd\x8d2\xca\xe6\xb3\xad\x99$\xff}\xa4\xa9*\xce5\xfcU\xf4\x96\xe4\x80\xb1\xb0K\x83\xb6,\x10\xc2\xb9\xbcG\xc8\x1a\x1a\x92\xa2\xef\x8f!b{\xf8\xd8\xa7\xb1\xee\xe1\x1e\x97\x11\xf0\xf4\x9a\na\xa3\xa8aXx{\x83.x\xc8\x0f\xd1\x88\xaa\x19g\xb22&\xfdx)\xb1s\xb3G\xfc<F\xd2\xc7\xbeQ\xa5\xf5D\xb5\x00\xfeE\x9c\x88o.\xe8\x9a\x9c\x11\x9cr\xef\xc3N \x8fI\x16\xcbS\x11\xf3\x84\x14 \xbe\xf2\xa0\x92H:\x02\xfa)\xc8\x1c\x8b\x839e\xa5]p\xd0+\xd0\'f\x8c\xd2\x9f8\x1e\xc3"\xf0\xd2\xc4)Y\x8c\xbfx\xcc\xe6\xca\xc6\xc9\xc4\xc5\xa9\xb1\xb3\x9fw\x1c\xb9\n&A\x1d\x86\xc9)>f\xaa/\xf4\xed\xdc\x86\x8b\xab\x1b\x89\xb0\\\xfb\x88\x8d\x8a=\x1c\x03\xf4\xdff|OR}\xcfr\xbc\x98\x8b\xe7t7\xb1\x9a\xbd\x8fz*\xd5\xb5\x18k[\x9bn\xfd>\xe0X\xf7K\x088\x16cs\xed0\x8d\xee\xcc-o`Q\x9f\x04\xcb\x87\xd0\x917p`Y\xa4O \xecf\t\xea,\x97Q\xb3\xa9k\xfe\xb0\xdf\xc6l\xa7\x89\xf0\xdc\xa5\x9aMM\xcd\xa5^&\r\r\x90\xad\x93\xf6\x19l\xb5W\xe6u\x19\xbe^N\x15\xdfJF\xfcP\xfa\xefnuO[\xe4,!\xcf\xe82r\xb2\x81\x06\xb1\xf8\x92\xd8\xe3>\xff\x1d\xe8\x9c\xcb\xeb\x07\xa4\xfe\x85\xf5&\xb6\xfcJrt;w\x80\xcc~a\xc2\xf7\x08\xffa\x99\x14,\xb6\x08k\xeb\x1d\xf4\xf6\xeb\xd5M\xa6\'\xa9j\xc9k\x0fP\xce\xd7,3\x1f\xcc\xddW:\x02\x03\xbb7\x18\xc54Q\xe50\xe2c(=\x85\x89,0\xd7\xaaJ+\x02\xb3/\xce\x0e\xd3\n\xc2N\xf7\x9bo\xb4\x19\xdb\xc8\x19\xb3\xd0}^\xdc\x80`D\x073}Z\x1d\x81-klf\xadt\xed\x97\xab3M\x97\x99\x11f\xab\xf3\x17\xd16\x8e\xb2eW\x851%0#\x06\t*\x86H\x86\xf7\r\x01\t\x151\x16\x04\x14\xecw|\xc23\rW\xad`\xbf0\x18\xe0\xb7\xc2\x1b\x15\xb0\x8b\xf2010!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14.\xa0\x17\x15I\xbb\xf1\x94;\x08$na\xc4\xb7;\xda\xaa\xdbQ\x04\x08\x9a\xba\x98\xec*6\xda`\x02\x02\x08\x00'
CERT_CONTENT_NOT_PASSWORD_ENCODED = b'0\x82\t\xb1\x02\x01\x030\x82\tw\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\th\x04\x82\td0\x82\t`0\x82\x04\x17\x06\t*\x86H\x86\xf7\r\x01\x07\x06\xa0\x82\x04\x080\x82\x04\x04\x02\x01\x000\x82\x03\xfd\x06\t*\x86H\x86\xf7\r\x01\x07\x010\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x060\x0e\x04\x08\x13\xba]\x97\x87\xd3\xaal\x02\x02\x08\x00\x80\x82\x03\xd0\xc0\xe5q\x11PP}\x18\x0f\x1a)\xba\xa5r\xb8Gx8\xb7\xda\xc2\xe7\x04\x03\x11\xafv?~H\xcb7\xe0,\xf5\xb5\\\x99\x81\xf1nS\x830\x94\xb9:p\r]\xa2\x0f"\xc3\xdf\xdf\xf3\xf5e\x03\xac\x12\xd01\xe1\xb2R\xcb\xdc\x9c\xd2\xc5\x9a"\xe8\x94\x10\xd0\x86 \x8df\x88\xbf\x87>\xc1=\x08p\x18\\\xd9D\x88\xdeS\xea\xa2\xa0\x0b\x1b^jr\xcf\x1f\x00JC"\xcb\x14\xa6P\xdc\x98\x0e\xe0-[\xc1\xbf\rn\xb4\x08\xa9\x89\xbf2\xf7r{\xd6\xd2\x08y\xd0\xda\x7fJ@\xb9[\x82\xe8\xadOD\x8d\xc7YY\xd4z\xd0\x9a\x8a\xae\x00[h\x90\xbb\xb7\xf4\xaf\x12U\r\xc2\xaencb\x9cH\xaf\xc9\x18\xb8\xca]\x90\xd6\r\x8e\xc0ij\xc1\x91\x00\x9c\x85\xb4\xda\xe1>\x178\x05\x93\x9dN\x03~{\xbe\xfa(*\'\x1b\xd1\xf7C\xcf\xe8lF\xec\xe5X\xc8l\xd9\xc8\x852\x0e\xf5\x8eP\x94 \xa9\xef\x00\xa5\xc2G\xbdx\xa3\x1f\x8e+\xcaS7R\x90\xcbr\x02\x00\\\xbe\x9b\xa9M\xa6L$\xa37\xd1\xa0\xcc\t\xc9\x11\xad\xe59\xba7\xf9=\x9d\x035\xca\xcb\xb7\xc6\xac7\x84o*\xe2\xca\xc2mhqqJ\xef\xac71\xbdg\xb9C\xc5\x97\xf1)|\x9c\x9e#\xa0\xf6b\xa4\x1cCHB\x98>\xa9=\xaaC\xc5\xf9\x86[\x02h\xdcKy\xb0\xd0\x029W\xcb\xf7\xd5d\x1ak\xf8\xba/\x14\x06\xc0\xa5\x15K(\xc7{\xa6C\xb2D#\xca\x88-Fkz\xd7=L`y\xaf\xf6#n/,\x96\x86\xafp\xee\x15\x7f\x03"\x93\xcd\x0e\xc5\xb1g\n\xda\xf7Md\x906\x96?\x07\xee\xb4\xabb\xd6\x95\x14\xd3\xcc\x073\x9a\xe0\xab\t\x9a\'\xfd\xb3\xd0tW#%_~\xd7\x07[F\x12\xd4fF\xe2m\x03\xe1\x19a\\\xee\xe7B\x7fe\\v@j\xf8\xd0\x8af\xc9\x82\xb0\x07\xa0\x93B\x90D\xd7e\xbdD\xc8\x0c-\x8c\xbe`\x0c\xa4\xad\xecX8\x96\x88\x87\xdc\x1f\xcc\xb8\xbfl\x01\xfc\xb8#S*\xe7\x9eU\x11\'0z\xf3H]q5\x0c\xea[\xca$\xa0C/I\xda\xfa\xfa\xe0\xa3\x1f\x1burdaP\xe7\x06\xbe\x87\x0b|\xd3\xa06\x1c\xfe\xab\x0c\xed.\xbd\xf9A1<\xcd9\xeb\x8e\xf8[\xd0\xd2\x9fO[\xe9\x19\xad\'\\\xfd\xc4\x05\x80\xe8\x95\x1a\x93f\x02\xa5\x1b\xd8\x9c\xba\x90\xc8\xe7\xbc\x036\xe1\xc4\x0f\xf7z\xdd\x18\xbe\xb4&\xec\xddQ~B7\x0f\x04\xef*\xdf\x1c\xf4\x84\xc8\xf7\xf2\x86\x0b\x9cv-\xd6.\x18@\xeb\xd7H7Y-\xce\x1f[\x91\x97\x07W\x15\x98\xffo\xc5\xb34\x97\x10J\x08\xb0<WL\x19\xf0\xfd\xf8\xd49\'\xaf\x95\xa1Km@\xd2\xab7o\xd1Z\xbf\x06\xd4P \xd3\xba\xf92\xffZ\xa1\x03\xa3\x1a\xc6\xa6\xed\xce7\x95\x9b\xb9\x98\'\xb4\xe7\t\x0b\xde\x1fB2\xdd\x11\xc4=\n\xf3\xace\x10sF\xc4\x05\xf8\xac\xb0g\x95bX!5B\xe5h5\xbd\n\x86\xd3\xe8\x9f\xa9a=2\xf3\x97\xe5\x83\xea\xadM\x95\xfa\xf4\xd6\x88\xe2fn\x87]a\x90\xa2\xe6m\\z\x80j.C\xbfW\x9a\x917\xfa\xf3rpD\r\xa2\xd6\xb9\xdf\x88\x14\xb3\xbe\xea\x17E@\x08\x91\xe7n\x08t\xe5\x08q\x92\x9fWw\xf2\xd2R\xdf\xba\xaf\xd9\xe2M\xafGY\x0f\x921\xd7\xd7\xba\xee\xa8\x82p7\x94\xc1\x9e;\x88\xb451d\\\rL6\xcf\x9e\xd1\x04\x19\xa8\xd5\xfc\n \xa3\xd3\xd8\xbaa\xe3\rU7H\x87[\x9f\xacA}bS\xbc\xca2\xe2\xb4uR%\x1b\x98\xeb\x94\x02\n\x93\xecK\x95 vO\xb9\xb5@\xf7\x1fiu\x8f\xf6@\xe5\xfe\xf7\xcfb]\x14@\x1c\x84\xf4K\xb0\xd4\nO\x1e=f\xfb\x12{\x1d\xa2\x90B^61\xc3\x06\xe3\x10f\xd5Yd;=\r\xd5P/\xf8\xb8\xf4\xc7;7\xef\xf1\xdf\xb0\x1c,\\~\r\xe9N)\x9d\x05\xe4\xb8"\x0c:k}O0\x82\x05A\x06\t*\x86H\x86\xf7\r\x01\x07\x01\xa0\x82\x052\x04\x82\x05.0\x82\x05*0\x82\x05&\x06\x0b*\x86H\x86\xf7\r\x01\x0c\n\x01\x02\xa0\x82\x04\xee0\x82\x04\xea0\x1c\x06\n*\x86H\x86\xf7\r\x01\x0c\x01\x030\x0e\x04\x08\xc1\x0f7d\x0e\xad$Z\x02\x02\x08\x00\x04\x82\x04\xc8t-\xe7v\x98\xf6\xca\xd8\x82\x02\xdfaD\x9e\x0f\xa1\x9c\x8en\xee\x10\x0eE\xdb\x8b=\xafqY\x17\x9d\x18E,\xedl\x92+\xa8gz\xa3+p\xe0\xb0\xc2"p\rpk\x82\x17u\x90\x8d\'D\x07\xa0\x01\xcb\xe2 \x99\xb9=8\x0b\x05\x03-|\xb7\x17\xe0\xd3\x95\x10o\x82X7s4^F2\xc2\x1f\x86\x94\xc9Yu\xcb\x19A\xa9\x17\xa8\x11\x92\x8f\xa92\x1b\x82}!(\x06>\x9b\xd2\xaa\x8ah\xed\xf5\x07\x8d\xcd\xd0\x8dg\x06\xd3\xb7x\xda\xee\xa5\x82B\xf1u\x01\xf6{\xea\xa2\x1d`>\xf4-\xe6k\x009\x01\x85\x80\xea\xc7"\x12\x82\xb3`\xe6d\x97\xb6mZ\x9bi$\x95\x83\xe7\x81\xed!>\xc44i\x073\xac\xb6,\xcf\x85\xc8\xc0\xb4k\x1a\x14\xb0V\xb0\xa0\xe6\xf3q\xb2K_oY~\x88s\xab\xdc\xad\xd7\xafY-\xc2\x83\x0b\\\xe9K\xa4t0\x84D\xe6\xbb8\xefn\xef\x1b\xd9\x89X\xc7\xad\x0e\x92 \xffg\xe4k\x89\xe4\x85\xfa\xf2\xd9j>>\x9f\xf4\xeb\x96\x94I\xf1\xdb@c\x19\xd8\xbc?\xce\x055\x12\x8f\xc1j\xef\x9fDG\xed\xfc4W\xfe\xc6i\x91\xdd.\x94\xf9[\xc6d<\xd1w\xfa!tR\x18>i\xa2\xad\xc1\xd7\xd7I\xa4\xa1\xe6%\xa8\x05&\xedH\x81q(\xbe:^\xc6\xb6\x04\x98@.\xcc\xb6\x87\xd7\x07LL\xc1\x95\x89a\xec\xc6\xef\xa0\xd3\xae\x8b\xb8v\xc1|\x948Ly\xc0:\x9d\r\xd9\xe5$q\xf3\xb7\xa0\x9d\xed\x871\xa7\xbde\xcc\xe2R\x80\x91B\xdc\x9c\x19P\x9ew\xca\x8b`\xabA\x82B$\xc8r"\'\x18b\xcf\xb4\xde\x0cW\xc4\xdc\x10\x8a\x16O\x9buH\xdd\xa9\xffr-h\xb6\x88u\xf5c\xf8\xa2}\xc3\xa9\x9e\n\xc9%>=\x9e9_0\xe0\xd4}4\xfaxrJ\x1c.\xca!a\x0c\xde\x97\xb8\x9d\x15X\x86Y\x12\xfa\x0fE\x8dS\x9a\xdd\xa9\xac\xff\xf5\x07R\xa4\xf7\xe9b\xb2\x1b\xd3$\xa9.gz\xea\x0bV\xe4&*\x08Z\xd7\xb5\x14J$\xb4+sCwUS\to\xcbZ\xf6\xcbU\x8b\xe4\xe4\xdd\x93\xac\x88\x10\xdb\xe6\xf7\xecGJB^\x96Fc[\xe2k\xfc\x1f]\xc9\x9d\xa8\xf7\xea\t\x1a\xe2\xd6\xf0\x9d\xa06,^ru\x89^V\xff\xb4\xfc&/\xb8\xb0.a_3\x9bp\xdb\xb2\xe7`\xeexu\xf5\'\xabM\x06\xe4\x93:\xca #\xf6.\xf7D\xb9\x19\xa3\x89j\xdb\xd1\xce\xb2\x88\xb8O{4\xe8\xaad9Xk"\xe7{V\x13\xc5w5\xad\xa6\xd7\x15\xf6\x06\xe2tr\xad_m=\xa1\x92\x80V\x05\xda\xe7\x7f\x03\xc8\xaa0\x9e\xa1\xf1\xdc\x8f2\x8d{4xYm\xcbP\x89\x8c\x13\xfd~\xe0/\x96\\\x8d\xa5K^\xb9\x9a\x03q.9g\twX\xeaO\xac\xbe}\xe6\x00p\xcb\x9c\x868\x00\xce%p7\xc3\r\xa8\xaa\xf9Sq\x9b\xf5\x97+^*\x08m\xde\x13$J\x0c\xb6\x98\x81\x98\x01\xad}\xbf\xe6J\xd0\xbcJ\xc6\xfc\x02\n@\xbel\xcb\xb2M\xdb\xa2iBf\x1eb;\x93IU"\xdf\xf9X\xfc\xf3\xf5\xc9\xef\t\xa8a\n\x8b\xcd\xff\xe0\xb4,\x8dql\xe4\xd6\xf6p\xe9\xd8W\xecoF\x82\xf5v\x01E\xff\xda\x99\x10\xa2\x1ec3\x07_\x04\xf3\x96\x80\xd3\x98w\x97\xb2\x97=\xd7$\xff\x1a\xca\x11\xe3\xdd\xbf\x87g-lo\x1f\x0e\xbd;\xab#\xb2\xc9\x9dWz\xba\xf9\xc6`a\x82\xd9\x00Iuo"\x1bd\x14\xd0ht\xf4\x1a\x1c\xdc\x98rk[\xbdK\xe9)\x7f\xf51\x1f\x984\xafr\xd1\x04{\x87\x19w\xca6\xf55\xea\xccMt\x92j\xed\xf1\xda\xa8E\xb6"6\xaeB83\xe2\x8a\xd8U\xb4$VB\xed\xda\x16\x82\xe4OJ(XF$\xf8\x85\x94\xeb\xf5\x90\xf2\xba\xbb*Fz\x05\x1f\tW\xad\x08\xddf\xd7-\xe8\xd3\xc9\xa4\xdf\xef\xd5L\xb7\xc9\xb2 D\xf9\x1a4\x9c\xee\xbf\xad[ \xd1\x08w\x14\xdfa\xae\xcb\x0e\xc5\xfb\xd9\xdd\x90\xc9U\xb8\x8e`\x07\xfc\xdf\xae\xc7\xd7\xeaz\x12B|{\xdb!z6\xb22\x84\x95\x9f\xfd\x99w4\xc6\xe7<\xa5\x07\x03\xeb\x19\x9218\xf8|/\x7f\x9c\x96\x921Y\x84\xd7\x8b\xab\xfe it$\xef!\x1dv:\x02\xa4\xdf\xdcZ\xc5c_\xc3qd[\x11.\xcd4\x02\x0f=\xf8\xd0\x1b\x81i+\xd9\xe7\xa3)\xc5\xc1\xf8\x8e\x13du^{\xc2\x0f)\xd1!\xf2\x06\xbaF\xd0\xc3\xf0e}V\x9c!\x9c\xeaC\x1d>J\xd4+n_`\xb2L\xc9|~\x051\xa1\xb6x\x91\xab\xa2F\xbe\x1d\n\x17y\x9f\xd0`\xa7\xb9\xafM\xaa\xe5\xeeM\xa7UzmH\x90\xe6h\xfb\xd9\xd0D\xe1\xb7\xe5\x85\xdb\x8f\x9a\xff\xb5\xeaW\xb7\xf2\x1e\x86\x14\xfdc\xaf\x10c\xd6\xdf\x86\xbb_\xc4yP\x95\x9a;\x06Sr\x9a\xa6~\x9f"\xc1\xaaQ\xb6\x0b\xd0\xa1p\x08K-\xb0+m\x1fKI\xca\xef\xd9\xe5\xaaxi\xe4\xa1\x1du1%0#\x06\t*\x86H\x86\xf7\r\x01\t\x151\x16\x04\x14\xecw|\xc23\rW\xad`\xbf0\x18\xe0\xb7\xc2\x1b\x15\xb0\x8b\xf2010!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14c\xc4?\x00\xdbG35r\x97\x86\xac\xad\x0f\xe5<\xa4cw`\x04\x08\xe0J/\xad\r\xf9F\x8a\x02\x02\x08\x00'


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


class CertificateClientTests(CertificatesTestCase, KeyVaultTestCase):

    def __init__(self, *args, **kwargs):
        super(CertificateClientTests, self).__init__(
            *args, replay_processors=[RetryAfterReplacer(), RequestUrlNormalizer()], **kwargs
        )

    def _import_common_certificate(self, client, cert_name):
        cert_password = "1234"
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
            certificate_name=cert_name,
            certificate_bytes=CERT_CONTENT_PASSWORD_ENCODED,
            policy=cert_policy,
            password=cert_password,
        )

    def _validate_certificate_operation(self, pending_cert_operation, vault, cert_name, original_cert_policy):
        self.assertIsNotNone(pending_cert_operation)
        self.assertIsNotNone(pending_cert_operation.csr)
        self.assertEqual(original_cert_policy.issuer_name, pending_cert_operation.issuer_name)
        pending_id = KeyVaultCertificateIdentifier(pending_cert_operation.id)
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

    @all_api_versions()
    @client_setup
    def test_crud_operations(self, client, **kwargs):
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

    @all_api_versions()
    @client_setup
    def test_import_certificate_not_password_encoded_no_policy(self, client, **kwargs):
        # If a certificate is not password encoded, we can import the certificate
        # without passing in 'password'
        certificate = client.import_certificate(
            certificate_name=self.get_resource_name("importNotPasswordEncodedCertificate"),
            certificate_bytes=CERT_CONTENT_NOT_PASSWORD_ENCODED,
        )
        self.assertIsNotNone(certificate.policy)

    @all_api_versions()
    @client_setup
    def test_import_certificate_password_encoded_no_policy(self, client, **kwargs):
        # If a certificate is password encoded, we have to pass in 'password'
        # when importing the certificate
        certificate = client.import_certificate(
            certificate_name=self.get_resource_name("importPasswordEncodedCertificate"),
            certificate_bytes=CERT_CONTENT_PASSWORD_ENCODED,
            password="1234",
        )
        self.assertIsNotNone(certificate.policy)

    @all_api_versions()
    @client_setup
    def test_list(self, client, **kwargs):
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

    @all_api_versions()
    @client_setup
    def test_list_certificate_versions(self, client, **kwargs):
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

    @all_api_versions()
    @client_setup
    def test_crud_contacts(self, client, **kwargs):
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

    @all_api_versions()
    @client_setup
    def test_recover_and_purge(self, client, **kwargs):
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
        deleted = [KeyVaultCertificateIdentifier(source_id=c.id).name for c in client.list_deleted_certificates()]
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
        deleted = [KeyVaultCertificateIdentifier(source_id=c.id).name for c in client.list_deleted_certificates()]
        self.assertTrue(not any(c in deleted for c in certs.keys()))

        # validate the recovered certificates
        expected = {k: v for k, v in certs.items() if k.startswith("livekvtestcertrec")}
        actual = {k: client.get_certificate_version(certificate_name=k, version="") for k in expected.keys()}
        self.assertEqual(len(set(expected.keys()) & set(actual.keys())), len(expected))

    @all_api_versions()
    @client_setup
    def test_async_request_cancellation_and_deletion(self, client, **kwargs):
        if self.is_live:
            pytest.skip("Skipping by default because of pipeline test flakiness: https://github.com/Azure/azure-sdk-for-python/issues/16333")

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

    @exclude_2016_10_01()
    @client_setup
    def test_policy(self, client, **kwargs):
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

    @all_api_versions()
    @client_setup
    def test_get_pending_certificate_signing_request(self, client, **kwargs):
        cert_name = self.get_resource_name("unknownIssuerCert")

        # get pending certificate signing request
        certificate = client.begin_create_certificate(
            certificate_name=cert_name, policy=CertificatePolicy.get_default()
        ).wait()
        pending_version_csr = client.get_certificate_operation(certificate_name=cert_name).csr
        self.assertEqual(client.get_certificate_operation(certificate_name=cert_name).csr, pending_version_csr)

    @exclude_2016_10_01()
    @client_setup
    def test_backup_restore(self, client, **kwargs):
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

    @all_api_versions()
    @client_setup
    def test_crud_issuer(self, client, **kwargs):
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

    @logging_enabled()
    @client_setup
    def test_logging_enabled(self, client, **kwargs):
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

    @logging_disabled()
    @client_setup
    def test_logging_disabled(self, client, **kwargs):
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

    @only_2016_10_01()
    @client_setup
    def test_models(self, client, **kwargs):
        """The client should correctly deserialize version 2016-10-01 models"""

        cert_name = self.get_resource_name("cert")
        cert = client.begin_create_certificate(cert_name, CertificatePolicy.get_default()).result()

        # these properties don't exist in version 2016-10-01
        assert cert.policy.key_curve_name is None
        assert cert.policy.certificate_transparency is None

    @all_api_versions()
    @client_setup
    def test_get_certificate_version(self, client, **kwargs):
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

    @only_2016_10_01()
    @client_setup
    def test_list_properties_of_certificates(self, client, **kwargs):
        """Tests API version v2016_10_01"""

        [_ for _ in client.list_properties_of_certificates()]

        with pytest.raises(NotImplementedError) as excinfo:
            [_ for _ in client.list_properties_of_certificates(include_pending=True)]

        assert "The 'include_pending' parameter to `list_properties_of_certificates` is only available for API versions v7.0 and up" in str(excinfo.value)

    @only_2016_10_01()
    @client_setup
    def test_list_deleted_certificates(self, client, **kwargs):
        """Tests API version v2016_10_01"""
        
        [_ for _ in client.list_deleted_certificates()]

        with pytest.raises(NotImplementedError) as excinfo:
            [_ for _ in client.list_deleted_certificates(include_pending=True)]

        assert "The 'include_pending' parameter to `list_deleted_certificates` is only available for API versions v7.0 and up" in str(excinfo.value)


def test_policy_expected_errors_for_create_cert():
    """Either a subject or subject alternative name property are required for creating a certificate"""
    client = CertificateClient("...", object())

    with pytest.raises(ValueError, match=NO_SAN_OR_SUBJECT):
        policy = CertificatePolicy()
        client.begin_create_certificate("...", policy=policy)

    with pytest.raises(ValueError, match=NO_SAN_OR_SUBJECT):
        policy = CertificatePolicy(issuer_name=WellKnownIssuerNames.self)
        client.begin_create_certificate("...", policy=policy)


def test_service_headers_allowed_in_logs():
    service_headers = {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
    client = CertificateClient("...", object())
    assert service_headers.issubset(client._client._config.http_logging_policy.allowed_header_names)


def test_custom_hook_policy():
    class CustomHookPolicy(SansIOHTTPPolicy):
        pass

    client = CertificateClient("...", object(), custom_hook_policy=CustomHookPolicy())
    assert isinstance(client._client._config.custom_hook_policy, CustomHookPolicy)
