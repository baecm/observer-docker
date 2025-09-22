import hashlib
import logging
import os
import random
import sys
import tempfile
import zipfile

import requests
import tqdm


logger = logging.getLogger(__name__)


def random_string(len: int = 8) -> str:
    return "".join(random.choice("0123456789ABCDEF") for _ in range(len))


def download_file(url: str, as_file: str) -> None:
    headers = {
        # python is sending some python User-Agent that Cloudflare doesn't like
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'
    }
    response = requests.get(url, allow_redirects=True, stream=True, headers=headers)
    logger.debug(f"downloading from {url} save as {as_file}")

    # Total size in bytes.
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 * 1024

    with open(as_file, 'wb') as f:
        tqdm_data = tqdm.tqdm(
            response.iter_content(block_size), file=sys.stderr,
            total=total_size / block_size, unit='MB', unit_scale=True
        )
        for data in tqdm_data:
            f.write(data)


def create_data_dirs(*dir_paths) -> None:
    for dir_path in dir_paths:
        os.makedirs(dir_path, mode=0o775, exist_ok=True)


def md5_file(fname: str) -> str:
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
