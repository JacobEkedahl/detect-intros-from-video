import os
import glob
import pprint
import subprocess
import sys
import shutil
import logging
import time
import datetime as dt
from pathlib import Path
import imageio_ffmpeg as ffmpeg
from moviepy.editor import VideoFileClip

import utils.file_handler as file_handler 

CAPTURE_TIME_IN_MIN = "8"
CUT_OFF_TIME = 480 # seconds
MAX_ATTEMPTS = 5

def get_new_files(startTime):
    newFiles = []
    for root, dirs, files in os.walk("temp/videos/"):  
        for file in files:
            path = os.path.join(root, file)
            st = os.stat(path)    
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            if mtime > startTime:
                out = os.path.join(root, file)
                newFiles.append(os.path.abspath(out))
    return newFiles


def merge_video_audio(video, audio):
    output = video.replace(".ts", "-converted.mp4")
    cmd = [ffmpeg._utils.get_ffmpeg_exe(), "-i", audio, "-i", video, "-c", "copy", "-t", "00:08:00.0", "-y", output]
    p = subprocess.Popen(cmd, shell=True) 
    p.wait()
    return output 
    

def cut_video(mp4, start, end):
    output = mp4.replace(".mp4", "-copy.mp4")
    cmd = [ffmpeg._utils.get_ffmpeg_exe(), "-i", mp4, "-ss", "%d" % start, "-t", "%d" % end, "-c", "copy", output]
    p = subprocess.Popen(cmd, shell=True) 
    p.wait()
    os.remove(mp4)
    newname = output.replace("-copy.mp4", "-converted.mp4")
    os.rename(output, newname)
    return newname


def download_files(url):
    timeBeforeDownload = dt.datetime.now()
    cmd = ["sh", "lib/runSvtPlay.sh", "--config", "lib/svtplay-dl.yaml", url, "--capture_time", CAPTURE_TIME_IN_MIN]
    try:
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        return get_new_files(timeBeforeDownload)
    except Exception as e:
        files = get_new_files(timeBeforeDownload)
        logging.error(e)
        for file in files: 
            os.remove(file)
        return []


def __try_to_download(url, attempt):
    if attempt >= MAX_ATTEMPTS:
        return []
    dl_files = download_files(url)
    if len(dl_files) == 0:
        logging.error("%s dl failure. Attempts: %d/%d)", url, attempt + 1, MAX_ATTEMPTS)
        time.sleep(attempt)
        return __try_to_download(url, attempt + 1)
    else: 
        logging.info("%s downlaoded {%s}", url, dl_files)
        return dl_files 


def download(url):
    dl_files = __try_to_download(url, 0)
    if len(dl_files) == 0:
        return None, None 
    audio = None 
    subs = None 
    video = None 
    mp4 = None 
    for file in dl_files:
        if file.endswith("audio.ts"):
            audio = file 
        elif file.endswith(".srt"):
            subs = file
        elif file.endswith(".ts"):
            video = file 
        elif file.endswith(".mp4"):
            mp4 = file 
        else:
            logging.error("%s failed. Could not read file: %s", url, file)
            for f in dl_files:
                os.remove(os.path.abspath(f))
            return None, None 
            
    if video != None and audio != None and mp4 == None: 
        mp4 = merge_video_audio(video, audio)

    if video != None:
        os.remove(os.path.abspath(video))

    if audio != None:
        os.remove(os.path.abspath(audio))

    # Cuts the film if in case that its longer than it should be
    clip = VideoFileClip(str(mp4))
    try:  
        duration = int(clip.duration)
        if  duration > CUT_OFF_TIME:
            clip.close()
            output = cut_video(mp4, 0, CUT_OFF_TIME)
            mp4 = output
        elif duration < CUT_OFF_TIME - 10:
            logging.error("%s duration was %d, expected %d.", url, duration, CUT_OFF_TIME)
            return None, None 
    finally:
        clip.close()

    delay = 0
    while file_handler.file_is_in_use(mp4): 
        time.sleep(1)
        delay = delay + 1
    if delay > 0:
        logging.warning("file %s was still in use for %d seconds", mp4, delay)

    head, filename = os.path.split(mp4)
    root, subdir = os.path.split(head) # /temp/videos
    showname = filename.split(".")[0]
     # move files to correct sub-directory based on show name
    if subdir != showname: 
        subdir = os.path.join(root, showname)
        Path(subdir).mkdir(parents=True, exist_ok=True)
        newfullpath = os.path.join(subdir, filename)
        os.rename(mp4, newfullpath)
        if subs:
            # move subtitles
            head, filename = os.path.split(subs)
            newfullpath = os.path.join(subdir, filename)
            os.rename(subs, newfullpath)
            subs = newfullpath

    return mp4, subs