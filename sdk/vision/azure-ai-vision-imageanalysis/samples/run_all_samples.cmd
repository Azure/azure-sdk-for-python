REM
REM A Windows script to run all Python samples in the folder, one after the other.
REM
echo on
python sample_analyze_all_image_file.py
python sample_caption_image_file.py
python async_samples\sample_caption_image_file_async.py
python sample_caption_image_url.py
python sample_dense_captions_image_file.py
python sample_objects_image_file.py
python sample_ocr_image_file.py
python sample_ocr_image_url.py
python async_samples\sample_ocr_image_url_async.py
python sample_people_image_file.py
python sample_smart_crops_image_file.py
python sample_tags_image_file.py
