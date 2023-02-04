# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class CallMediaClient(object):
    def __init__(self,
                 endpoint,
                 **kwargs
    ):
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint

        self._client = CallMediaService(
            
        )

    def play(PlaySource play):
        # TODO
        return True

    def play_to_all():
        # TODO
        return True

    def start_recognizing():
        # TODO
        return True
        
    def cancel_all_media_operations():
        # TODO
        return True
