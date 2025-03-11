from typing import Any

class ClassNameClient:
    def __init__(self, credential: str, *, eight: str = None) -> None:
        """
        Initializes a new instance of the class.
        
        :param credential: The credential to use for authentication.
        :type credential: str
        :param eight: The eighth parameter.
        :type eight: str
        """
        self.credential = credential
        self.eight = eight
