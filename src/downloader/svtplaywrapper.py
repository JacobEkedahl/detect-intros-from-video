import os
import pprint
import subprocess
import sys
from pathlib import Path

import numpy as np

import utils.file_handler as file_handler

from . import videoMerger


def download_video(url, name_folder):
    download_path = file_handler.get_full_path_folder(name_folder)
    print(download_path)
    command = ["sh", "lib/runSvtPlay.sh", url, "--subfolder", "--output", download_path]
    output = subprocess.call(command, shell=True) 
    videoMerger.mergeImageAndAudio(download_path)
    print(output)

def download_videos(urls, name_folder):
    download_path = file_handler.get_full_path_folder(name_folder)
    command = ["sh", "lib/runSvtPlay.sh"] + urls + ["--config", "lib/svtplay-dl.yaml", "--subfolder", "--output", download_path]
    output = subprocess.call(command, shell=True)
    print(output)

def start_download(urls, name_folder, number_of_episodes):
    num_epi = int(number_of_episodes)
    if (num_epi < 1):
        print("specify number of episodes")
        exit()
    if num_epi < len(urls):
        urls = urls[:-len(urls)+num_epi]

    for url in urls:
        download_video(url, name_folder)

def start(name_textfile, name_folder, number_of_episodes):
    urls = file_handler.get_all_urls_from_file(name_textfile)
    start_download(urls, name_folder, number_of_episodes)
