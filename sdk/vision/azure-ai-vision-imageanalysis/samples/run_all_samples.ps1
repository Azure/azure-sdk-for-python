# A PowerShell script to run all Python samples in the folder, one after the other.
$python = if ($env:OS -eq "Windows_NT") { "python" } else { "python3" }

Write-Host "===> sample_analyze_all_image_file.py"
Start-Process -NoNewWindow -Wait $python sample_analyze_all_image_file.py

Write-Host "===> sample_caption_image_file.py"
Start-Process -NoNewWindow -Wait $python sample_caption_image_file.py

Write-Host "===> sample_caption_image_file_async.py"
Start-Process -NoNewWindow -Wait $python async_samples/sample_caption_image_file_async.py

Write-Host "===> sample_caption_image_url.py"
Start-Process -NoNewWindow -Wait $python sample_caption_image_url.py

Write-Host "===> sample_dense_captions_image_file.py"
Start-Process -NoNewWindow -Wait $python sample_dense_captions_image_file.py

Write-Host "===> sample_objects_image_file.py"
Start-Process -NoNewWindow -Wait $python sample_objects_image_file.py

Write-Host "===> sample_ocr_image_file.py"
Start-Process -NoNewWindow -Wait $python sample_ocr_image_file.py

Write-Host "===> sample_ocr_image_url.py"
Start-Process -NoNewWindow -Wait $python sample_ocr_image_url.py

Write-Host "===> sample_ocr_image_url_async.py"
Start-Process -NoNewWindow -Wait $python async_samples/sample_ocr_image_url_async.py

Write-Host "===> sample_people_image_file.py"
Start-Process -NoNewWindow -Wait $python sample_people_image_file.py

Write-Host "===> sample_smart_crops_image_file.py"
Start-Process -NoNewWindow -Wait $python sample_smart_crops_image_file.py

Write-Host "===> sample_tags_image_file.py"
Start-Process -NoNewWindow -Wait $python sample_tags_image_file.py
