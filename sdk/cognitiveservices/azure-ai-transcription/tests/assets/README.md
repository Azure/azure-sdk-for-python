# Test Assets

This directory contains test audio files used for transcription testing.

## Current Test Files

- `audio.wav` - Primary test audio file used by `test_transcribe_with_audio_file` tests

## Adding More Test Audio Files

You can add additional audio files to this directory for different test scenarios:

- `audio_multi_speaker.wav` - Audio with multiple speakers for diarization testing
- `audio_multilingual.wav` - Audio containing multiple languages
- `audio_long.wav` - Longer audio for performance testing
- `audio_noisy.wav` - Audio with background noise
- Any other `.wav` or `.mp3` files for specific test cases

## Audio File Requirements

- Format: WAV, MP3, FLAC, or other supported formats
- Size: < 250 MB
- Duration: < 2 hours (preferably < 30 seconds for unit tests)
- Sample rate: 8 kHz or 16 kHz recommended
- Channels: Mono or stereo

## Note on Binary Files

Audio files should be small test files only. Do not commit large audio files to the repository.
Consider using `.gitattributes` to handle binary files properly.

## Example Test Audio

For initial testing, you can use publicly available test audio or generate simple audio files using text-to-speech tools.
