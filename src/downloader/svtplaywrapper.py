import os
import pprint
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

import utils.file_handler as file_handler

from . import videoMerger


def download_video(url):
    command = ["sh", "lib/runSvtPlay.sh", "--config", "lib/svtplay-dl.yaml", url]
    try:
        output = subprocess.check_call(command, shell=True) 
    except:
        print("error while downloading, retrying..")
        time.sleep(1)
        download_video(url)
    print(output)
    attempts = 0
    while attempts < 3:
        try:
            return videoMerger.mergeImageAndAudio()
        except:
            print("error while merging, retrying..")
            time.sleep(1)
            attempts += 1

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
