
def generate_shared_access_signature(topic_hostname, shared_access_key, expiration_date, **kwargs):
    # type: (str, str, datetime.Datetime, Any) -> str
    """ Helper method to generate shared access signature given hostname, key, and expiration date.
        :param str topic_hostname: The topic endpoint to send the events to.
        :param str shared_access_key: The shared access key to be used for generating the token
        :param datetime.datetime expiration_date: The expiration date for the signature.
        :rtype: str
    """
    pass
