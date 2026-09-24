# Release History

## 1.0.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

- Python 3.8 is no longer supported. Please use Python version 3.9 or later.

## 1.0.0 (2024-10-18)

### Other Changes

First stable release. No changes compared to previous beta release (1.0.0b3).

## 1.0.0b3 (2024-07-26)

### Features Added

Added support for Entra ID authentication.

## 1.0.0b2 (2024-02-09)

### Breaking Changes

- In the previous version, you would call the `analyze` method on the `ImageAnalysisClient` to analyze an image from a publicly accessible URL, or from a memory buffer. To better align with other Azure client libraires, this was changed in this release. Call the new dedicated `analyze_from_url` method to analyze an image from URL. Keep calling the `analyze` method to analyze an image from a memory buffer.

## 1.0.0b1 (2024-01-09)

- Azure Image Analysis client library for Python. Uses the generally available [Computer Vision REST API (2023-10-01)](https://learn.microsoft.com/azure/ai-services/computer-vision/overview-image-analysis).
