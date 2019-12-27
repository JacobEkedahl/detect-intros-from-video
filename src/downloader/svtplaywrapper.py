import os
import pprint
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

import utils.file_handler as file_handler
from moviepy.editor import VideoFileClip

from . import videoMerger


def download_video(url):
    command = ["sh", "lib/runSvtPlay.sh", "--config", "lib/svtplay-dl.yaml", url, "--capture_time", "8"]
    if try_to_download(0, command) is None:
        return None
    return try_to_merge()

def try_to_download(tries, command):
    if tries > 3:
        return None
    try:
        attempts = 0
        output = subprocess.check_call(command, shell=True) 
        print("result of download: " + str(output))
        while output == '0' and attempts < 3:
            attempts += 1
            print("wasnt able to download, retrying..")
            time.sleep(1)
            output = subprocess.check_call(command, shell=True) 
    except:
        print("error while downloading and calling subprocess, retrying..")
        time.sleep(1)
        try_to_download(tries +1, command)
    return True

def try_to_merge():
    attempts = 0
    while attempts < 3:
        try:
            video_path = videoMerger.mergeImageAndAudio()
            clip = VideoFileClip(str(video_path))
            video_length = int(clip.duration)
            if video_length < 400:
                print('error after merging, size of videofile is under 400 seconds, trying again..')
                os.remove(video_path)
                time.sleep(1)
                attempts += 1
            else:
                return video_path
        except:
            print("error while merging, retrying..")
            time.sleep(1)
            attempts += 1
    return None

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
