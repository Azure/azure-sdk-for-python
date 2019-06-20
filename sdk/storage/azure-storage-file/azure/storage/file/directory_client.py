# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class DirectoryClient():
    """
    A client to interact with the sirectory.
    """

    def __init__(
            self, share_name=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            credential=None, # type: Optional[Any]
            configuration=None # type: Optional[Configuration]
        ):
        # type: (...) -> DirectoryClient
        """Creates a new DirectoryClient. This client represents interaction with a specific
        directory, although it may not yet exist.
        :param share_name: The directory with which to interact. If specified, this value will override
         a directory value specified in the directory URL.
        :type share_name: str or ~azure.storage.file.models.DirectoryProperties
        :param str directory_path: The full URI to the directory.
        :param credential:
        :param configuration: A optional pipeline configuration.
         This can be retrieved with :func:`DirectoryClient.create_configuration()`
        """
    
    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share_name=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            configuration=None, # type: Optional[Configuration]
            **kwargs # type: Any
        ):
        # type: (...) -> DirectoryClient
        """
        Create DirectoryClient from a Connection String.
        """
    
    def get_file_client(self, file_name):
        """Get a client to interact with the specified file.
        The file need not already exist.

        :param directory_name:
            The name of the directory.
        :type directory_name: str
        :returns: A File Client.
        :rtype: ~azure.core.file.file_client.FileClient
        """

    def get_subdirectory_client(self, directory_name):
        """Get a client to interact with the specified subdirectory.
        The subdirectory need not already exist.

        :param directory_name:
            The name of the subdirectory.
        :type directory_name: str
        :returns: A Directory Client.
        :rtype: ~azure.core.file.directory_client.DirectoryClient
        """

    def create_directory(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Any]
        """Creates a new Directory.
        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """

    def delete_directory(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> None
        """Marks the specified directory for deletion. The directory is
        later deleted during garbage collection.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """

    def list_directies_and_files(self, prefix=None, timeout=None, **kwargs):
        # type: (Optional[str], Optional[int]) -> DirectoryProperties
        """
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties 
        """

    def get_directory_properties(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> DirectoryProperties
        """
        :returns: DirectoryProperties
        """

    def set_directory_metadata(self, metadata, timeout=None, **kwargs):
        # type: (Dict[str, Any], Optional[int], Any) ->  Dict[str, Any]
        """ Sets the metadata for the directory.
        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: directory-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """

    def create_subdirectory(
            self, directory_name,  # type: str,
            metadata=None, #type: Optional[Dict[str, Any]]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> DirectoryClient
        """Creates a new Sub Directory.
        :param directory_name:
            The name of the subdirectory.
        :type directory_name: str
        :param metadata:
            Name-value pairs associated with the directory as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: DirectoryClient
        :rtype: DirectoryClient
        """

    def delete_subdirectory(
            self, directory_name,  # type: str,
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> None
        """Deletes a Sub Directory.
        :param directory_name:
            The name of the subdirectory.
        :type directory_name: str
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: None
        """

    def create_file(
            self, file_name,  # type: str,
            size, # type: int
            content_settings=None, # type: Any
            metadata=None, #type: Optional[Dict[str, Any]]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> FileClient
        """Creates a new file.
        :param file_name:
            The name of the file.
        :type file_name: str
        :param size:
            The max size of the file.
        :type size: int
        :param content_settings:
            The content settings.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: FileClient
        :rtype: FileClient
        """

    def delete_file(
            self, file_name,  # type: str,
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> None
        """Deletes a file.
        :param file_name:
            The name of the file.
        :type file_name: str
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: None
        """
