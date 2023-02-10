cd .\sdk\ml\azure-ai-ml\
Get-Location | select -ExpandProperty Path
venv/Scripts/python.exe Scripts\switch_to_playback_mode.py
venv/Scripts/pytest.exe $Args[0] --no-header --disable-warnings
cd .\..\..\..\