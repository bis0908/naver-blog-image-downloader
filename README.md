# Naver Blog Image Downloader

A CLI tool to download images from Naver blog posts by extracting images from specific HTML classes.

## Features

- Downloads images from Naver blog posts
- Targets specific HTML classes: `se-section-image` and `se-section-imageGroup`
- Handles both absolute and relative image URLs
- Creates download directory if it doesn't exist
- Provides detailed progress feedback
- Generates sequential filenames to avoid conflicts

## Installation

1. Install Python 3.8 or higher
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the program:

```bash
python main.py
```

The program will prompt you for:
1. The Naver blog URL to scrape
2. The local directory path where images should be saved

## Example

```
=== Naver Blog Image Downloader ===

Enter the Naver blog URL: https://blog.naver.com/example/post
Enter the path to save images: ./downloaded_images

Processing URL: https://blog.naver.com/example/post
Save directory: /path/to/downloaded_images

ℹ Fetching blog page...
ℹ Parsing HTML content...
ℹ Found 2 sections with class 'se-section-image'
ℹ Found 1 sections with class 'se-section-imageGroup'
ℹ Found 5 unique images
Found 5 images to download.

ℹ Downloading 1/5: 001_example_image.jpg
ℹ Downloading 2/5: 002_photo.png
ℹ Downloading 3/5: 003_screenshot.jpg
ℹ Downloading 4/5: 004_diagram.png
ℹ Downloading 5/5: 005_chart.jpg

✓ Successfully downloaded all 5 images!
```

## File Structure

- `main.py` - Main CLI application entry point
- `scraper.py` - HTML scraping and parsing functionality
- `downloader.py` - Image downloading functionality
- `utils.py` - Utility functions for user interaction and logging
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.8+
- requests
- beautifulsoup4
- urllib3