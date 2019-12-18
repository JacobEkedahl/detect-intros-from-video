import os
import pprint
import subprocess
import sys
from pathlib import Path

import numpy as np

import utils.file_handler as file_handler

from . import videoMerger


def download_video(url):
    command = ["sh", "lib/runSvtPlay.sh", "--config", "lib/svtplay-dl.yaml", url]
    output = subprocess.call(command, shell=True) 
    print(output)
    return videoMerger.mergeImageAndAudio()

def start_download(urls, number_of_episodes):
    num_epi = int(number_of_episodes)
    if (num_epi < 1):
        print("specify number of episodes")
        exit()
    if num_epi < len(urls):
        urls = urls[:-len(urls)+num_epi]
    for url in urls:
        download_video(url)

def start(name_textfile, number_of_episodes):
    urls = file_handler.get_all_urls_from_file(name_textfile)
    start_download(urls, number_of_episodes)
