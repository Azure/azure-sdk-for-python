# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class FileClient():
    """
    A client to interact with the file.
    """
    def __init__(
            self, file_url,  # type: str
            share_name=None,  # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credentials=None,  # type: Optional[Any]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> FileClient
        """ Creates a new FileClient. This client represents interaction with a specific
        file, although that file may not yet exist.
        :param str file_url: The full URI to the file.
        :param share_name: The share with which to interact. If specified, this value will override
         a share value specified in the share URL.
        :type share_name: str or ~azure.storage.file.models.ShareProperties
        :param credentials:
        :param configuration: A optional pipeline configuration.
        """
    
    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share_name=None, # type: Optional[Union[str, ShareProperties]]
            directory_path=None, # type: Optional[str]
            file_name=None, # type: Optional[str]
            configuration=None, # type: Optional[Configuration]
            **kwargs # type: Any
        ):
        # type: (...) -> FileClient
        """
        Create FileClient from a Connection String.
        """

    def create_file(
            self, source_url, # type: str
            metadata=None,  # type: Optional[Dict[str, str]]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Any]
        """Creates a new FileClient.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int quota:
            The quota to be alloted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """

    def upload_file(
            self, data, # type: Any
            size=None, # type: Optional[int]
            content_settings=None, # type: Optional[ContentSettings]
            metadata=None,  # type: Optional[Dict[str, str]]
            validate_content=False,  # type: bool
            max_connections=1,  # type: Optional[int]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Any]
        """Uploads a new file.
        :param data:
            Data of the file.
        :type data: Any
        :param size:
            The max size of the file.
        :type size: int
        :param content_settings:
            The content settings
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param validate_content:
            If the content is validated or not.
        :type validate_content: bool
        :param int max_connections:
            The max_connections to be alloted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """

    def copy_from_url(
            self, source_url, # type: str
            metadata=None,  # type: Optional[Dict[str, str]]
            timeout=None # type: Optional[int]
        ):
        # type: (...) -> Any
        """Creates a new FileClient.
        :param metadata:
            Name-value pairs associated with the file as metadata.
        :type metadata: dict(str, str)
        :param int quota:
            The quota to be alloted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Polling object in order to wait on or abort the operation
        :rtype: Any
        """

    def download_file(
            self, start_range=None,  # type: Optional[int]
            end_range=None, # type: Optional[int]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: bool
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Iterable[bytes]
        """
        :returns: A iterable data generator (stream)
        """

    def download_file_to_stream(
            self, start_range=None,  # type: Optional[int]
            end_range=None, # type: Optional[int]
            length=None,  # type: Optional[int]
            validate_content=False,  # type: bool
            max_connections=1,  # type: Optional[int]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> FileProperties
        """
        :returns: FileProperties
        """

    def delete_file(self, timeout=None, **kwargs):
        # type: (Optional[int], Optional[Any]) -> None
        """Marks the specified file for deletion. The file is
        later deleted during garbage collection.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """

    def get_file_properties(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> FileProperties
        """
        :returns: FileProperties
        """

    def set_http_headers(self, content_settings, timeout=None):
        #type: (ContentSettings, Optional[int]) -> Dict[str, Any]
        """
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any) 
        """

    def set_file_metadata(self, metadata=None, timeout=None):
        #type: (Optional[Dict[str, Any]], Optional[int]) -> Dict[str, Any]
        """
        :returns: File-updated property dict (Etag and last modified).
        :rtype: dict(str, Any) 
        """

    def update_ranges(
            self, start_range=None, # type: Optional[int]
            end_range=None, # type: Optional[int]
            validate_content=False, # type: Optional[bool]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> List[dict[str, int]]
        """
        Returns the list of valid ranges of a file.
        :param int start_range:
            Start of byte range to use for getting valid page ranges.
            If no end_range is given, all bytes after the start_range will be searched.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param int end_range:
            End of byte range to use for getting valid page ranges.
            If end_range is given, start_range must be provided.
            This range will return valid page ranges for from the offset start up to
            offset end.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param validate_content:
            If the content is validated or not.
        :type validate_content: bool
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A list of page ranges.
        """

    def get_ranges(
            self, start_range=None, # type: Optional[int]
            end_range=None, # type: Optional[int]
            timeout=None, # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> List[dict[str, int]]
        """
        Returns the list of valid ranges of a file.
        :param int start_range:
            Start of byte range to use for getting valid page ranges.
            If no end_range is given, all bytes after the start_range will be searched.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param int end_range:
            End of byte range to use for getting valid page ranges.
            If end_range is given, start_range must be provided.
            This range will return valid page ranges for from the offset start up to
            offset end.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-, etc.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: A list of page ranges.
        """
    
    def clear_range(
            self, start_range,  # type: int
            end_range,  # type: int
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> Dict[str, Any]
        """
        :param int start_range:
            Start of byte range to use for writing to a section of the file.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :param int end_range:
            End of byte range to use for writing to a section of the file.
            Pages must be aligned with 512-byte boundaries, the start offset
            must be a modulus of 512 and the end offset must be a modulus of
            512-1. Examples of valid byte ranges are 0-511, 512-1023, etc.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """

    def resize_file(self, size, timeout=None):
        # type: (int, Optional[int]) -> Dict[str, Any]
        """Resizes a file to the specified size.
        :param int size:
            Size to resize file to.
        :param str timeout:
            The timeout parameter is expressed in seconds.
        :returns: File-updated property dict (Etag and last modified).
        :rtype: Dict[str, Any]
        """
