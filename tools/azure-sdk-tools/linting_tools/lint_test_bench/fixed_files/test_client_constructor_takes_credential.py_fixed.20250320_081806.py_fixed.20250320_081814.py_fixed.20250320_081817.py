class ClassNameClient:
    def __init__(self, credential: str, **kwargs) -> None:
        """
        :param credential: The credential to use.
        :type credential: str
        :keyword api_version: The API version to use.
        :paramtype api_version: str
        """
        self.credential: str = credential
        self.api_version: str = kwargs.get('api_version', '2018')
