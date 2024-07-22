---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-computer-vision
urlFragment: image-analysis-samples
---

# Samples for Image Analysis client library for Python

These are runnable console Python programs that show how to use the Image Analysis client library.

- They cover all the supported visual features.
- Most use the synchronous client to analyze an image file or image URL. Three samples (located in the `async_samples` folder) use the asynchronous client.
- Most use API key authentication. Two samples (having `_entra_id_auth` in their name) use Entra ID authentication.

The concepts are similar, you can easily modify any of the samples to your needs.

## Synchronous client samples

|**File Name**|**Description**|
|----------------|-------------|
|[sample_analyze_all_image_file.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_analyze_all_image_file.py) | Extract all 7 visual features from an image file, using a synchronous client. Logging turned on.|
|[sample_caption_image_file.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_caption_image_file.py) and [sample_caption_image_url.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_caption_image_url.py)| Generate a human-readable sentence that describes the content of an image file or image URL, using a synchronous client.|
|[sample_caption_image_file_entra_id_auth.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_caption_image_file_entra_id_auth.py) | Generate a human-readable sentence that describes the content of an image file, using a synchronous client and Entra ID authentication.|
|[sample_dense_captions_image_file.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_dense_captions_image_file.py) | Generating a human-readable caption for up to 10 different regions in the image, including one for the whole image, using a synchronous client.|
|[sample_ocr_image_file.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_ocr_image_file.py) and [sample_ocr_image_url.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_ocr_image_url.py)|  Extract printed or handwritten text from an image file or image URL, using a synchronous client.|
|[sample_tags_image_file.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_tags_image_file.py) | Extract content tags for thousands of recognizable objects, living beings, scenery, and actions that appear in an image file, using a synchronous client.|
|[sample_objects_image_file.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_objects_image_file.py) | Detect physical objects in an image file and return their location, using a synchronous client. |
|[sample_smart_crops_image_file.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_smart_crops_image_file.py) | Find a representative sub-region of the image for thumbnail generation, using a synchronous client.|
|[sample_people_image_file.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_people_image_file.py) | Locate people in the image and return their location, using a synchronous client.|

## Asynchronous client samples

|**File Name**|**Description**|
|----------------|-------------|
|[sample_caption_image_file_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/async_samples/sample_caption_image_file_async.py) | Generate a human-readable sentence that describes the content of an image file, using an asynchronous client. |
|[sample_ocr_image_url_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/async_samples/sample_ocr_image_url_async.py) | Extract printed or handwritten text from an image URL, using an asynchronous client. |
|[sample_ocr_image_url_entra_id_auth_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/async_samples/sample_ocr_image_url_entra_id_auth_async.py) | Extract printed or handwritten text from an image URL, using an asynchronous client and Entra ID authentication |

## Prerequisites

See [Prerequisites](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/README.md#prerequisites) here.

## Setup

* Clone or download this sample repository
* Open a command prompt / terminal window in this samples folder
* Install the Image Analysis client library for Python with pip:
  ```bash
  pip install azure-ai-vision-imageanalysis
  ```
* If you plan to run the asynchronous client samples, insall the additional package [aiohttp](https://pypi.org/project/aiohttp/):
  ```bash
  pip install aiohttp
  ```

## Set environment variables

See [Set environment variables](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/README.md#set-environment-variables) here.

## Running the samples

To run the first sample, type:
```bash
python sample_analyze_all_image_file.py
```
similarly for the other samples.

## Example console output

The sample `sample_analyze_all_image_file.py` analyzes the image `sample.jpg` in this folder:

![sample JPEG image](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample.jpg)

And produces an output similar to the following:

```
Image analysis results:
 Caption:
   'a person wearing a mask sitting at a table with a laptop', Confidence 0.8498
 Dense Captions:
   'a person wearing a mask sitting at a table with a laptop', {'x': 0, 'y': 0, 'w': 864, 'h': 576}, Confidence: 0.8498
   'a person using a laptop', {'x': 293, 'y': 383, 'w': 195, 'h': 100}, Confidence: 0.7724
   'a person wearing a face mask', {'x': 383, 'y': 233, 'w': 275, 'h': 336}, Confidence: 0.8209
   'a close-up of a green chair', {'x': 616, 'y': 211, 'w': 164, 'h': 249}, Confidence: 0.8763
   'a person wearing a colorful cloth face mask', {'x': 473, 'y': 294, 'w': 68, 'h': 56}, Confidence: 0.7086
   'a person using a laptop', {'x': 288, 'y': 211, 'w': 151, 'h': 244}, Confidence: 0.7642
   'a person wearing a colorful fabric face mask', {'x': 433, 'y': 240, 'w': 180, 'h': 236}, Confidence: 0.7734
   'a close-up of a laptop on a table', {'x': 115, 'y': 443, 'w': 476, 'h': 125}, Confidence: 0.8537
   'a person wearing a mask and using a laptop', {'x': 0, 'y': 0, 'w': 774, 'h': 432}, Confidence: 0.7816
   'a close up of a text', {'x': 714, 'y': 493, 'w': 130, 'h': 80}, Confidence: 0.6407
 Read:
   Line: 'Sample text', Bounding box [{'x': 721, 'y': 502}, {'x': 843, 'y': 502}, {'x': 843, 'y': 519}, {'x': 721, 'y': 519}]
     Word: 'Sample', Bounding polygon [{'x': 722, 'y': 503}, {'x': 785, 'y': 503}, {'x': 785, 'y': 520}, {'x': 722, 'y': 520}], Confidence 0.9930
     Word: 'text', Bounding polygon [{'x': 800, 'y': 503}, {'x': 842, 'y': 502}, {'x': 842, 'y': 519}, {'x': 800, 'y': 520}], Confidence 0.9890
   Line: 'Hand writing', Bounding box [{'x': 720, 'y': 525}, {'x': 819, 'y': 526}, {'x': 819, 'y': 544}, {'x': 720, 'y': 543}]
     Word: 'Hand', Bounding polygon [{'x': 721, 'y': 526}, {'x': 759, 'y': 526}, {'x': 759, 'y': 544}, {'x': 721, 'y': 543}], Confidence 0.9890
     Word: 'writing', Bounding polygon [{'x': 765, 'y': 526}, {'x': 819, 'y': 527}, {'x': 819, 'y': 545}, {'x': 765, 'y': 544}], Confidence 0.9940
   Line: '123 456', Bounding box [{'x': 721, 'y': 548}, {'x': 791, 'y': 548}, {'x': 791, 'y': 563}, {'x': 721, 'y': 564}]
     Word: '123', Bounding polygon [{'x': 723, 'y': 548}, {'x': 750, 'y': 548}, {'x': 750, 'y': 564}, {'x': 723, 'y': 564}], Confidence 0.9940
     Word: '456', Bounding polygon [{'x': 761, 'y': 548}, {'x': 788, 'y': 549}, {'x': 787, 'y': 564}, {'x': 760, 'y': 564}], Confidence 0.9990
 Tags:
   'furniture', Confidence 0.9874
   'clothing', Confidence 0.9793
   'person', Confidence 0.9427
   'houseplant', Confidence 0.9400
   'desk', Confidence 0.9183
   'indoor', Confidence 0.8964
   'laptop', Confidence 0.8782
   'computer', Confidence 0.8482
   'sitting', Confidence 0.8135
   'wall', Confidence 0.7512
   'woman', Confidence 0.7411
   'table', Confidence 0.6811
   'plant', Confidence 0.6445
   'using', Confidence 0.5359
 Objects:
   'chair', {'x': 603, 'y': 225, 'w': 152, 'h': 224}, Confidence: 0.6180
   'person', {'x': 399, 'y': 244, 'w': 249, 'h': 325}, Confidence: 0.8810
   'Laptop', {'x': 295, 'y': 387, 'w': 211, 'h': 102}, Confidence: 0.7670
   'chair', {'x': 441, 'y': 436, 'w': 256, 'h': 136}, Confidence: 0.5810
   'dining table', {'x': 123, 'y': 437, 'w': 460, 'h': 125}, Confidence: 0.6060
 People:
   {'x': 395, 'y': 241, 'w': 261, 'h': 333}, Confidence 0.9603
   {'x': 831, 'y': 246, 'w': 31, 'h': 255}, Confidence 0.0017
 Smart Cropping:
   Aspect ratio 0.9: Smart crop {'x': 238, 'y': 0, 'w': 511, 'h': 568}
   Aspect ratio 1.33: Smart crop {'x': 54, 'y': 0, 'w': 760, 'h': 571}
 Image height: 576
 Image width: 864
 Model version: 2023-10-01
```

## Troubleshooting

See [Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/README.md#troubleshooting) here.


