# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import urllib
import logging
from typing import Optional
from aiohttp import ClientTimeout
from aiohttp_retry import RetryClient

from azure.ai.generative.synthetic.simulator._model_tools.identity_manager import KeyVaultAPITokenManager


ENDPOINT_URL = "https://lasertag-vision.cognitiveservices.azure.com/"
FEATURE_NAMES = ["tags", "objects", "caption", "denseCaptions", "read", "smartCrops", "people"]  # Excluding: None
LANGUAGE = "en"  # Alternatives: "zh", "ja", "pt", "es"


def build_description(result_data: dict, min_confidence: float) -> str:
    '''Given a JSON response from the Computer Vision API, build a description of the image in natural language.'''
    description = result_data['captionResult']['text']

    # Parse tags
    def collect_tags(obj: dict) -> str:
        return ', '.join([tag['name'] for tag in obj['tags'] if tag['confidence'] > min_confidence])
    objects = [collect_tags(obj) for obj in result_data['objectsResult']['values']]

    text = repr(result_data['readResult']['content'])
    lines = [text['content'] for text in result_data['readResult']['pages'][0]['lines']]
    denseCaptions = [caption['text'] for caption in result_data['denseCaptionsResult']['values'] if caption['confidence'] > min_confidence]
    image_width = result_data['metadata']['width']
    image_height = result_data['metadata']['height']
    tags = [tag['name'] for tag in result_data['tagsResult']['values'] if tag['confidence'] > min_confidence]
    people = len([person for person in result_data['peopleResult']['values'] if person['confidence'] > min_confidence])

    description = [
        f"Image with {image_width}x{image_height} pixels",
        f"description: {description}",
        f"captions: {', '.join(denseCaptions)}",
        f"objects: {', '.join(objects)}",
        f"text: {text}",
        f"text lines: {', '.join(lines)}",
        f"tags: {', '.join(tags)}",
        f"people: {people}"
    ]

    return '\n'.join(description)


async def azure_cognitive_services_caption(
    session: RetryClient,
    token_manager,
    kv_token_manager: KeyVaultAPITokenManager,
    image_url: Optional[str] = None,
    image_data: Optional[bytes] = None,
    tag_confidence_thresh: float = 0.2,
    timeout: int = 10
) -> str:
    '''Request the Computer Vision API to analyze an image, then build a natural
    language description from the response.'''

    # Build request
    params = urllib.parse.urlencode({
        "features": ','.join(FEATURE_NAMES),
        "language": LANGUAGE
    })
    url = f'{ENDPOINT_URL}computervision/imageanalysis:analyze?api-version=2023-02-01-preview&{params}'
    headers = {
        "Content-Type": "application/json" if image_url is not None else "application/octet-stream",
        "Ocp-Apim-Subscription-Key": await kv_token_manager.get_token(),
        "Authorization": f'Bearer {await token_manager.get_token()}'
    }

    # Add image either as url or upload it in binary
    if image_url is not None:
        body = json.dumps({"url": image_url})
    elif image_data is not None:
        body = image_data
    else:
        raise ValueError('Must provide either image_url or image_path')

    # Send request
    async with session.post(
        url,
        headers=headers,
        data=body,
        params=params,
        timeout=ClientTimeout(total=timeout)
    ) as response:
        if response.status == 200:
            response_data = await response.text()
            response_data = json.loads(str(response_data))

            return build_description(response_data, tag_confidence_thresh)

        else:
            raise Exception(f"Received unexpected HTTP status: {response.status} {await response.text()}")

