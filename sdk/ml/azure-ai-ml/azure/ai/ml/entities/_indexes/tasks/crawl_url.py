# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
import re
import threading
import time
import traceback
from contextlib import contextmanager
from http import HTTPStatus
from urllib.parse import urljoin, urlparse

import requests
from azure.ai.ml.entities._indexes.tasks.crack_and_chunk import str2bool
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)
from bs4 import BeautifulSoup

logger = get_logger("crawl_url")

_azure_logger = logging.getLogger("azure.core.pipeline")
_azure_logger.setLevel(logging.WARNING)

ALLOWED_EXTENSIONS = [".txt", ".md", ".html", ".pdf", ".docx", ".pptx"]


class MaxTimeExceeded(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def terminate():
        raise MaxTimeExceeded()

    timer = threading.Timer(seconds, terminate)
    timer.start()
    try:
        yield
    finally:
        timer.cancel()


def try_get_extension_for_media_type(url, media_type):
    if media_type == "text/plain":
        return ".txt"
    elif media_type == "text/html":
        return ".html"
    elif media_type == "application/pdf":
        return ".pdf"
    else:
        _, extension = os.path.splitext(url)
        if extension in ALLOWED_EXTENSIONS:
            return extension

    return None


def add_links_from_html(html, original_url, links, logger, support_http=False):
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a"):
        url = link.get("href")
        if url:
            url = url.strip().lower()
            if url.startswith("http://") and support_http and url not in links or url.startswith("https://") and url not in links:
                links.append(url)
            elif url.startswith("mailto:"):
                logger.info(f"Skipping mailto link {url}")
                continue
            elif "://" not in url and not url.startswith("#") and not url.startswith("javascript:"):
                # try to resolve absolute url
                try:
                    absolute_url = urljoin(original_url, url)
                    if absolute_url not in links:
                        links.append(absolute_url)
                except:
                    logger.info(f"Skipping invalid url {url}")
                    continue


def get_unique_written_file_name(url, extension, writtenFiles):
    base, _ = os.path.splitext(url)
    parsed_url = urlparse(base)
    if not parsed_url.path:
        base = "index"

    # Remove query params
    if "?" in base:
        base = base[: base.index("?")]

    # Replace invalid chars
    base = re.sub(r"[^\w_. -]+", "_", base)
    base = re.sub(r"\/+", "_", base)

    # Strip and ensure name not empty
    base = base.strip().strip("_")
    if len(base) == 0:
        base = "index"

    # Ensure unique
    attempt = 0
    attemptedFilename = f"{base}{extension}"
    while attemptedFilename in writtenFiles:
        attempt += 1
        attemptedFilename = f"{base}_{attempt}{extension}"
    writtenFiles.add(attemptedFilename)
    return attemptedFilename


def download(url, destination, writtenFiles, links, logger, redirectsRemaining, maxFileSize, supportHttp=False):
    # Fetch URL
    r = requests.get(url)
    if r.status_code == HTTPStatus.MOVED_PERMANENTLY and r.headers.get("location") and redirectsRemaining > 0:
        return download(r.headers.get("location"), destination, writtenFiles, links, redirectsRemaining - 1)
    elif r.status_code != HTTPStatus.OK:
        logger.info(f"Skipping url {url} with status code {r.status_code}")
        return

    # Get extension
    extension = try_get_extension_for_media_type(url, r.headers.get("content-type"))
    if extension is None:
        logger.info(f"Skipping unsupported url {url} with media type {r.headers.get('content-type')}")
        return

    # Check content length
    content_length = r.headers.get("content-length")
    if content_length and int(content_length) > maxFileSize:
        logger.info(f"Skipping url {url} with content length {content_length}")
        return

    data = r.content
    if len(data) > maxFileSize:
        logger.info(f"Skipping url {url} with size {len(data)}")
        return

    # Extract nested links
    if links and extension.lower() == ".html":
        # Extract links from html
        html = data.decode("utf-8")
        add_links_from_html(html, url, links, logger, supportHttp)

    # Write file
    filename = get_unique_written_file_name(url, extension, writtenFiles)
    os.makedirs(destination, exist_ok=True)
    output_dest = os.path.join(destination, filename)

    logger.info(f"Writing file {filename} to {output_dest}")
    with open(output_dest, "wb") as f:
        f.write(data)


def crawl_url(args, logger):
    try:
        logger.info(f"Starting crawl with args: {json.dumps(args, indent=2)}")
        max_crawl_time = args.get("max_crawl_time", 60)
        max_crawl_depth = args.get("max_crawl_depth", 0)
        max_files = args.get("max_files", 1000)
        max_redirects = args.get("max_redirects", 3)
        max_download_time = args.get("max_download_time", 15)
        max_file_size = args.get("max_file_size", 5000000)
        support_http = args.get("support_http", False)
        output_path = args.get("output_path", None)
        url = args.get("url", None)

        if not url or not output_path:
            raise ValueError("url and output_path are required")

        with time_limit(max_crawl_time):
            writtenFiles = set()
            links = [url]
            redirectsRemaining = max_redirects

            linkIndex = 0
            for level in range(max_crawl_depth + 1):
                logger.info(f"Starting crawl level {level} with {len(links)} links")
                # Determine last file in this depth to crawl
                endLinkIndex = min(len(links), max_files)  # Don't crawl more than max_files
                if endLinkIndex <= linkIndex:
                    # If reached max number of files, or no more links, then done.
                    break

                # Crawl all links in this depth
                for link in links[linkIndex:endLinkIndex]:
                    logger.info(f"Crawling link {link}")
                    try:
                        with time_limit(max_download_time):
                            download(
                                link,
                                output_path,
                                writtenFiles,
                                links,
                                logger,
                                redirectsRemaining,
                                max_file_size,
                                supportHttp=support_http,
                            )
                    except MaxTimeExceeded:
                        logger.info(f"Max download time of {max_download_time} seconds exceeded. Stopping.")
                        return
                pass
    except MaxTimeExceeded:
        logger.info(f"Max crawl time of {max_crawl_time} seconds exceeded. Stopping.")
        return


def main_wrapper(args, logger):
    with track_activity(logger, "crawl_url") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            crawl_url(args, logger)
        except Exception:
            activity_logger.error(
                f"crawl_url failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--max_files", type=int, default=1000, help="Maximum number of files for crawler to download.")
    parser.add_argument(
        "--max_crawl_time", type=int, default=60, help="Maximum download time in seconds for the overall crawl."
    )
    parser.add_argument(
        "--max_download_time", type=int, default=15, help="Maximum download time in seconds for any single file."
    )
    parser.add_argument("--max_file_size", type=int, default=5000000, help="Maximum file size for crawler to download.")
    parser.add_argument(
        "--max_crawl_depth",
        type=int,
        default=1,
        help="Maximum depth for crawler to follow links. 0 doesn't crawl any nested links.",
    )
    parser.add_argument(
        "--max_redirects", type=int, default=3, help="Maximum number of redirects for crawler to follow."
    )
    parser.add_argument("--support_http", type=str2bool, default=False, help="Whether to support http links.")
    parser.add_argument(
        "--output_path", type=str, required=True, help="Output path for the crawler to write the downloaded files."
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        help="Defaults to 1, which will log aggregate information about documents and IDs of deleted documents. 2 will log all document_ids as they are processed.",
    )
    args = parser.parse_args()

    print("\n".join(f"{k}={v}" for k, v in vars(args).items()))

    enable_stdout_logging()
    enable_appinsights_logging()

    try:
        main_wrapper(vars(args), logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
