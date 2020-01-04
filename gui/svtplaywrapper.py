import os
import pprint
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

import file_handler
import videoMerger
from moviepy.editor import VideoFileClip


def download_video(url):
    command = ["sh", "gui/lib/runSvtPlay.sh", "--config", "gui/lib/svtplay-dl.yaml", url, "--capture_time", "8"]
    if try_to_download(command) is None:
        return None
    attempts = 0
    video_file = try_to_merge()
    if video_file == None:
        while attempts < 3:
            video_file = try_to_merge()
            attempts += 1
    return video_file

def try_to_download(command):
    attemps = 0
    while attemps < 3:
        try:
            output = subprocess.check_call(command, shell=True) 
            return True
        except:
            print("error while downloading and calling subprocess, retrying.. #" + str(attemps))
            time.sleep(1)
            newCommand = command[:]
            if "--force" not in command:
                newCommand.append("--force")
                command = newCommand
            attemps += 1
    return None

def try_to_merge():
    try:
        video_path = videoMerger.mergeImageAndAudio()
        clip = VideoFileClip(str(video_path))
        video_length = int(clip.duration)
        if video_length < 400:
            print('error after merging, size of videofile is under 400 seconds, trying again..')
            os.remove(video_path)
            time.sleep(1)
        else:
            return video_path
    except:
        print("error while merging, retrying..")
        time.sleep(1)
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
