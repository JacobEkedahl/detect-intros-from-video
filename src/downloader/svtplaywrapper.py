import os
import pprint
import subprocess
import sys
from pathlib import Path

import numpy as np

from . import videoMerger

# ---  will save videos in outputDir which is under under home directory ---

def download_video(url, name_folder):
    download_path = os.path.join(str(Path.home()), name_folder)
    command = ["sh", "lib/runSvtPlay.sh", url, "--config", "lib/svtplay-dl.yaml", "--output", download_path]
    print(command)
    output = subprocess.call(command, shell=True) 
    videoMerger.mergeImageAndAudio(download_path)
    print(output)

def download_videos(urls, name_folder):
    download_path = os.path.join(str(Path.home()), name_folder)
    command = ["sh", "lib/runSvtPlay.sh"] + urls + ["--config", "lib/svtplay-dl.yaml", "--output", download_path]
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
       # print(url)
        download_video(url, name_folder)

def start(name_textfile, name_folder, number_of_episodes):
    text_file_path = os.path.join(str(Path.home()), name_textfile)
    urls = [line.rstrip('\n') for line in open(text_file_path)]
    start_download(urls, name_folder, number_of_episodes)
