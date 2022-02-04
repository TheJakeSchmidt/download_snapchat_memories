import argparse
import collections
import datetime
import os
from pprint import pprint
import subprocess
import sys
import urllib

from bs4 import BeautifulSoup
import dateparser
import pyexif
import pytz
import requests
import tqdm


def download_snapchat_memories(mydata_path):
    output_directory = os.path.abspath('snapchat_memories')
    os.makedirs(output_directory, exist_ok=True)

    print(f'{datetime.datetime.now()} - Downloading Snapchat memories from {mydata_path} into {output_directory}')
    memories_html = get_memories_html(mydata_path)
    timestamps_str, urls = extract_timestamps_and_urls(memories_html)
    for row_number, (timestamp_str, download_url) in tqdm.tqdm(
            list(enumerate(zip(timestamps_str, urls))), desc='Downloading'):
        filename = download_memory(download_url, row_number, output_directory)
        if filename is not None:
            fix_exif_timestamp(os.path.join(output_directory, filename), timestamp_str)


def get_memories_html(mydata_path):
    if not os.path.exists(mydata_path):
        raise Exception(f'{mydata_path} doesn\'t exist')
    memories_html_path = os.path.join(mydata_path, 'html', 'memories_history.html')
    if not os.path.exists(memories_html_path):
        raise Exception(f'{os.path.abspath(mydata_path)} does not contain a memories_history.html file')
    with open(memories_html_path, 'r') as f:
        memories_html = f.read()
    return memories_html


def extract_timestamps_and_urls(memories_html):
    soup = BeautifulSoup(memories_html, 'html.parser')
    tables = soup.find_all('table')
    if len(tables) != 1:
        raise Exception('Multiple <table> tags found in {memories_html_path}')
    rows = tables[0].find_all('tr')
    non_header_rows = [row for row in rows if not any([child.name == 'th' for child in row.children])]
    timestamps_str = [list(row.children)[0].text for row in non_header_rows]
    links = [list(row.children)[2].a.get('href') for row in non_header_rows]
    for link in links:
        if not link.startswith('javascript:downloadMemories('):
            raise Exception(f'Download link does not look like the right format: {link}')
    urls = [link[len('javascript:downloadMemories(')+1:-3] for link in links]
    return timestamps_str, urls


def download_memory(download_url, row_number, output_directory):
    api_url, data = download_url.split('?')
    real_url = requests.post(api_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}).text
    if not real_url:
        print(f'{datetime.datetime.now()} - WARNING: No URL returned from {api_url} for data {data} (row {row_number} in memories_history.html)')
        return None
    filename = os.path.basename(urllib.parse.urlparse(real_url).path)
    subprocess.run(['curl', '--silent', real_url, '-o', os.path.join(output_directory, filename)], check=True)
    return filename


def fix_exif_timestamp(path, timestamp_str):
    timestamp = dateparser.parse(timestamp_str).astimezone(pytz.timezone('America/New_York'))
    exif_editor = pyexif.ExifEditor(path)
    exif_editor.setOriginalDateTime(timestamp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mydata_path', required=True,
        help='The path to a folder unzipped from the mydata_1234567890123.zip file emailed to you by Snapchat')
    args = parser.parse_args()

    download_snapchat_memories(os.path.abspath(args.mydata_path))
