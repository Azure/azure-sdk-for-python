# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy
import os

from azure.maps.render.models import TextFormat, IncludeText, MapImageryStyle, RasterTileFormat, StaticMapLayer, MapImageStyle, MapTileSize, TilesetID, TileSize, TileFormat, MapTileLayer, MapTileStyle
from azure.maps.render import RenderClient


def write_stream_to_file(stream, filename: str):
    with open(filename, "wb") as file:
        bytes = bytearray()
        for line in stream:
            bytes.extend(line)
        file.write(bytes)
    # open file
    os.system('start {}'.format(filename))


parser = argparse.ArgumentParser(
    description='Render Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.add_argument('--stateset_id', action="store", required=True)
stateset_id = args_parsed = parser.parse_args().stateset_id


client = RenderClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))

result = client.render.get_copyright_caption(TextFormat.JSON)
print(result)


result = client.render.get_copyright_for_tile(TextFormat.JSON, 6, 9, 22)
print(result)


result = client.render.get_copyright_for_world(TextFormat.JSON)
print(result)


result = client.render.get_copyright_from_bounding_box(
    TextFormat.JSON, "52.41064,4.84228", "52.41072,4.84239", IncludeText.YES)
print(result)


result = client.render.get_map_imagery_tile(
    RasterTileFormat.PNG, MapImageryStyle.SATELLITE, 6, 10, 22)
write_stream_to_file(
    result, "tmp/map_imagery_tile.png")


result = client.render.get_map_state_tile_preview(6, 10, 22, stateset_id)
write_stream_to_file(result, "tmp/state_tile.json")


result = client.render.get_map_static_image(RasterTileFormat.PNG, StaticMapLayer.BASIC,
                                            MapImageStyle.DARK, 2, None, "1.355233,42.982261,24.980233,56.526017")
write_stream_to_file(result, "tmp/static_image.png")


result = client.render.get_map_tile(TileFormat.PNG, MapTileLayer.BASIC,
                                    MapTileStyle.MAIN, 6, 10, 22, MapTileSize.FIVE_HUNDRED_TWELVE)
write_stream_to_file(result, "tmp/tile.png")


result = client.render_v2.get_map_tile_preview(
    TilesetID.MICROSOFT_BASE, 6, 10, 22, tile_size=TileSize.FIVE_HUNDRED_TWELVE)
write_stream_to_file(result, "tmp/tile_v2.vec")
