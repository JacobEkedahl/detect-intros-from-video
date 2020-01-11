import threading
import os
import glob
import subprocess
import sys
import shutil
import logging
import time 
from pathlib import Path
import imageio_ffmpeg as ffmpeg
from moviepy.editor import VideoFileClip

from utils import file_handler, constants

TEMP_FOLDER_PATH = constants.TEMP_FOLDER_PATH
VIDEO_FOLDER_PATH = constants.VIDEO_FOLDER_PATH
LENGTH_IN_SECONDS = constants.VIDEO_START_LEN
CAPTURE_TIME_IN_MIN = str(int(LENGTH_IN_SECONDS/60))
TEMP_DL_FOLDER = "dl_temp"
MAX_ATTEMPTS_ON_FAILURE = 3

def __get_all_unmerged_files(path):
    files = []
    types = ["*.audio.ts", "*.m4a"] #find audio files and match with videofiles
    for ext in types:
        audioExtNoStar = ext[1:]
        for audioName in Path(path).rglob(ext):
            audioName = str(audioName)
            videoName = audioName.replace(audioExtNoStar, audioVideoTranslator[audioExtNoStar], 1)
            fileName = audioName.replace(audioExtNoStar,  '', 1)
            files.append(FileInfo(fileName, audioName, videoName ))
    return files

audioVideoTranslator = {".audio.ts": ".ts", ".m4a": ".mp4"}

class FileInfo:
    def __init__(self, fileName, audioName, videoName):
        self.fileName = fileName
        self.audioName = audioName
        self.videoName = videoName


def __merge_video_audio(f_info):
    output = f_info.fileName + "-converted.mp4"
    cmd = [ffmpeg._utils.get_ffmpeg_exe(), "-i", f_info.audioName, "-i", f_info.videoName, "-c", "copy", "-t", "00:08:00.0", "-y", output]
    subprocess.call(cmd, shell=True)
    os.remove(f_info.audioName)
    os.remove(f_info.videoName)
    return output 


def __get_files_in_dir(path):
    result = []
    for x in os.walk(path):
        for y in glob.glob(os.path.join(x[0], '*.*')):
            result.append(y)
    return result 


def __get_video_and_subtitles(path):
    subtitles = None
    video = None
    for f in __get_files_in_dir(path):
        if f.endswith(".mp4"):
            video = f
        elif f.endswith(".srt"):
            subtitles = f 
    return video, subtitles


def __move_file_to_dest(source, target):
    try: 
        os.rename(source, target)
    except FileExistsError as e: 
        logging.warning(e)


def download_files(url):
    id = threading.get_ident()
    dirname = "%s/%s%s" % (TEMP_FOLDER_PATH, TEMP_DL_FOLDER, id)
    os.mkdir(dirname)
    cmd = ["sh", "lib/runSvtPlay.sh", "--config", "lib/svtplay-dl.yaml", url, "--capture_time", CAPTURE_TIME_IN_MIN, "--output", dirname]
    try:
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        for f_info in __get_all_unmerged_files(dirname):
            __merge_video_audio(f_info)

        video, subtitles = __get_video_and_subtitles(dirname)
            
        head, filename = os.path.split(video)
        showname = filename.split(".")[0]
        newroot = os.path.join(VIDEO_FOLDER_PATH, showname)

        Path(newroot).mkdir(parents=True, exist_ok=True) # if not exists create: VIDEO_FOLDER_PATH/showname
        
        # Move files to proper sub-directory
        new_video_dest = os.path.join(newroot, filename)
        new_subs_dest = new_video_dest.replace(".mp4", ".srt")

        
        __move_file_to_dest(video, new_video_dest)
        video = new_video_dest
        if subtitles != None:
            __move_file_to_dest(subtitles, new_subs_dest)
            subtitles = new_subs_dest

        try:  # Verify video length 
            clip = VideoFileClip(str(video))
            videolength = int(clip.duration)
            if videolength < LENGTH_IN_SECONDS - 10:
                raise Exception("Video length is too short: %d." % videolength)
        finally: 
            clip.close()

        return video, subtitles

    except Exception as e: 
        logging.exception(e)
        return None, None # failed 
        
    finally: 
        try: 
            shutil.rmtree(dirname) # delete the temp dl folder 
        except Exception as e: 
            logging.exception(e)


def try_to_dl_files(url, max_attempts):
    for attempts in range(1, max_attempts):
        try: 
            video, subs = download_files(url)
            if video != None:
                return video, subs
        except Exception as e: 
            logging.warning("Download failed #%02d sleep(%d)\nException: %s" % (1, attempts, e))
        time.sleep(1)
    raise Exception("Failed to download after %d attempts" % max_attempts)


# Backward compatability, only returns the video file 
def download_video(url):
    try: 
        video, subs = try_to_dl_files(url, MAX_ATTEMPTS_ON_FAILURE)
        return video 
    except Exception as e:
        logging.exception(e)
        return None 

 