class ClassNameClient:
    def __init__(self, api_version: str = "2018", **kwargs) -> None:
        """
        :param api_version: The API version to use.
        :type api_version: str
        """
        self.api_version = api_version
