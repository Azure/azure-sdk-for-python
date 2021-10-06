# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import validators

class CallingServerUtils(object):

    @staticmethod
    def is_valid_url(
        url # type: str
    ): # type: (...) -> bool
        result = validators.url(url)

        if isinstance(result, validators.utils.ValidationFailure):
            return False

        return True

    @staticmethod
    def parse_length_from_content_range(content_range):
        '''
        Parses the content length from the content range header: bytes 1-3/65537
        '''
        if content_range is None:
            return None

        # First, split in space and take the second half: '1-3/65537'
        # Next, split on slash and take the second half: '65537'
        # Finally, convert to an int: 65537
        return int(content_range.split(' ', 1)[1].split('/', 1)[1])

    @staticmethod
    def validate_and_format_range_headers(start_range, end_range):
        # If end range is provided, start range must be provided
        if (end_range is not None) and start_range is None:
            raise ValueError("start_range value cannot be None.")

        # Format based on whether end_range is present
        range_header = None
        if end_range is not None:
            range_header = 'bytes={0}-{1}'.format(start_range, end_range)
        elif start_range is not None:
            range_header = "bytes={0}-".format(start_range)

        return range_header
