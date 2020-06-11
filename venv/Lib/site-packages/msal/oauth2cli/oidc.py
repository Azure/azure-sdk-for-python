import json
import base64
import time

from . import oauth2

def decode_part(raw, encoding="utf-8"):
    """Decode a part of the JWT.

    JWT is encoded by padding-less base64url,
    based on `JWS specs <https://tools.ietf.org/html/rfc7515#appendix-C>`_.

    :param encoding:
        If you are going to decode the first 2 parts of a JWT, i.e. the header
        or the payload, the default value "utf-8" would work fine.
        If you are going to decode the last part i.e. the signature part,
        it is a binary string so you should use `None` as encoding here.
    """
    raw += '=' * (-len(raw) % 4)  # https://stackoverflow.com/a/32517907/728675
    raw = str(
        # On Python 2.7, argument of urlsafe_b64decode must be str, not unicode.
        # This is not required on Python 3.
        raw)
    output = base64.urlsafe_b64decode(raw)
    if encoding:
        output = output.decode(encoding)
    return output

base64decode = decode_part  # Obsolete. For backward compatibility only.

def decode_id_token(id_token, client_id=None, issuer=None, nonce=None, now=None):
    """Decodes and validates an id_token and returns its claims as a dictionary.

    ID token claims would at least contain: "iss", "sub", "aud", "exp", "iat",
    per `specs <https://openid.net/specs/openid-connect-core-1_0.html#IDToken>`_
    and it may contain other optional content such as "preferred_username",
    `maybe more <https://openid.net/specs/openid-connect-core-1_0.html#Claims>`_
    """
    decoded = json.loads(decode_part(id_token.split('.')[1]))
    err = None  # https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
    if issuer and issuer != decoded["iss"]:
        # https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfigurationResponse
        err = ('2. The Issuer Identifier for the OpenID Provider, "%s", '
            "(which is typically obtained during Discovery), "
            "MUST exactly match the value of the iss (issuer) Claim.") % issuer
    if client_id:
        valid_aud = client_id in decoded["aud"] if isinstance(
            decoded["aud"], list) else client_id == decoded["aud"]
        if not valid_aud:
            err = "3. The aud (audience) Claim must contain this client's client_id."
    # Per specs:
    # 6. If the ID Token is received via direct communication between
    # the Client and the Token Endpoint (which it is in this flow),
    # the TLS server validation MAY be used to validate the issuer
    # in place of checking the token signature.
    if (now or time.time()) > decoded["exp"]:
        err = "9. The current time MUST be before the time represented by the exp Claim."
    if nonce and nonce != decoded.get("nonce"):
        err = ("11. Nonce must be the same value "
            "as the one that was sent in the Authentication Request")
    if err:
        raise RuntimeError("%s id_token was: %s" % (
            err, json.dumps(decoded, indent=2)))
    return decoded


class Client(oauth2.Client):
    """OpenID Connect is a layer on top of the OAuth2.

    See its specs at https://openid.net/connect/
    """

    def decode_id_token(self, id_token, nonce=None):
        """See :func:`~decode_id_token`."""
        return decode_id_token(
            id_token, nonce=nonce,
            client_id=self.client_id, issuer=self.configuration.get("issuer"))

    def _obtain_token(self, grant_type, *args, **kwargs):
        """The result will also contain one more key "id_token_claims",
        whose value will be a dictionary returned by :func:`~decode_id_token`.
        """
        ret = super(Client, self)._obtain_token(grant_type, *args, **kwargs)
        if "id_token" in ret:
            ret["id_token_claims"] = self.decode_id_token(ret["id_token"])
        return ret

    def build_auth_request_uri(self, response_type, nonce=None, **kwargs):
        """Generate an authorization uri to be visited by resource owner.

        Return value and all other parameters are the same as
        :func:`oauth2.Client.build_auth_request_uri`, plus new parameter(s):

        :param nonce:
            A hard-to-guess string used to mitigate replay attacks. See also
            `OIDC specs <https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest>`_.
        """
        return super(Client, self).build_auth_request_uri(
            response_type, nonce=nonce, **kwargs)

    def obtain_token_by_authorization_code(self, code, nonce=None, **kwargs):
        """Get a token via auhtorization code. a.k.a. Authorization Code Grant.

        Return value and all other parameters are the same as
        :func:`oauth2.Client.obtain_token_by_authorization_code`,
        plus new parameter(s):

        :param nonce:
            If you provided a nonce when calling :func:`build_auth_request_uri`,
            same nonce should also be provided here, so that we'll validate it.
            An exception will be raised if the nonce in id token mismatches.
        """
        result = super(Client, self).obtain_token_by_authorization_code(
            code, **kwargs)
        nonce_in_id_token = result.get("id_token_claims", {}).get("nonce")
        if "id_token_claims" in result and nonce and nonce != nonce_in_id_token:
            raise ValueError(
                'The nonce in id token ("%s") should match your nonce ("%s")' %
                (nonce_in_id_token, nonce))
        return result

