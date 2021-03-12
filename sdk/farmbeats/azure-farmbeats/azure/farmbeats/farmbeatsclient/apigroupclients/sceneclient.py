import time
from datetime import datetime, timedelta
import re
from urllib.parse import unquote as url_decode
import requests
import os
import errno

FILE_LINK_TO_FILE_PATH_RE = r"^.*filePath=([^&$]+).*$"


class SceneClient():
    def __init__(
        self,
        farmbeats_client,
        farmbeats_credential
    ):
        self.client = farmbeats_client
        self.credential = farmbeats_credential

    def get_all(
        self,
        farmer_id,
        boundary_id,
        provider="Microsoft",
        source="Sentinel_2_L2A",
        start_date=None,
        end_date=None,
        max_cloud_coverage_percentage=100,
        max_dark_pixel_coverage_percentage=100,
        image_names=None,
        image_resolutions=None,
        image_formats=None
        # limit = 1000
    ):
        return self.client.get_scenes(
            farmer_id,
            boundary_id,
            provider,
            source,
            start_date,
            end_date,
            max_cloud_coverage_percentage,
            max_dark_pixel_coverage_percentage,
            image_names,
            image_resolutions,
            image_formats,
            1000
        ).value

    def download_scene_data(
        self,
        file_link,
    ):

        def ensure_dirs(filename):
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise


        file_path = re.match(FILE_LINK_TO_FILE_PATH_RE, file_link).group(1)

        # actual wizardry

        local_file_path = "~/farmbeats/temp/scene_download/" + url_decode(file_path)
        local_file_abs_path = os.path.expanduser(local_file_path)
        ensure_dirs(local_file_abs_path)
        headers = {
            'User-Agent': 'Python SDK', # Figure out if there is some way to standarize that in the client as well,
            'Authorization': 'Bearer ' + self.credential.get_token("https://farmbeats.azure.net/.default").token,
        }
        with requests.get(file_link, stream=True, headers=headers) as r:
            r.raise_for_status()
            with open(local_file_abs_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk:
                    f.write(chunk)
        
        return local_file_abs_path

            
        

