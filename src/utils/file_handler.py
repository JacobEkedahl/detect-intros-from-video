import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from . import constants as c

TEMPFOLDERNAME = "temp"
VIDEOFOLDERNAME = "videos"
URLSTEXTFILENAME = "video-serier.txt"

def norm_path(full_path):
    return os.path.normpath(full_path)

def create_folderstructure_if_not_exists():
    if not os.path.exists(get_full_path_videos()):
        os.makedirs(get_full_path_videos())

def get_framespaths_from_video(video_file):
    dir = get_dir_for_frames(video_file)
    result = []
    for file in os.listdir(dir):
        if isfile(join(dir, file)):
            file_info = file.replace('.jpg', '').split('-')
            result.append(
                FrameInfo(
                    str(os.path.join(dir, file)),
                    float(file_info[0]),
                    int(file_info[1])))
    return result

def get_file_name_frame(video_file, count, sec):
    dir = get_dir_for_frames(video_file)
    return str(os.path.join(dir, str(count)+ "-" +str(sec) +".jpg"))

def get_all_other_videos_in_series(video_file):
    result = []
    parent_dir = os.path.dirname(video_file)
    for file in os.listdir(parent_dir):
        if file.endswith(".mp4"):
            result.append(str(os.path.join(parent_dir,file)))
    result.remove(video_file)
    return result

def is_dir_for_frames_empty(video_file):
    dir = get_dir_for_frames(video_file)
    return len(os.listdir(path=dir)) == 0

def get_all_urls_from_file(file_name):
    text_file_path = norm_path(os.path.join(get_full_path_temp(), file_name))
    urls = [line.rstrip('\n') for line in open(text_file_path)]
    return [item for item in urls if item.startswith("http")]

def get_all_mp4_files():
    files = []
    for filename in Path(get_full_path_videos()).rglob('*.mp4'):
        files.append(str(filename))
    return files

def get_all_unmerged_files():
    files = []
    types = ["*.audio.ts", "*.m4a"] #find audio files and match with videofiles

    for ext in types:
        audioExtNoStar = ext[1:]
        for audioName in Path(get_full_path_videos()).rglob(ext):
            audioName = str(audioName)
            print("audioname: " + audioName)
            videoName = audioName.replace(audioExtNoStar, audioVideoTranslator[audioExtNoStar], 1)
            fileName = audioName.replace(audioExtNoStar,  '', 1)
            files.append(FileInfo(fileName, audioName, videoName ))
    return files

# Helper functions
def get_full_path_folder(folder_name):
    return norm_path(os.path.join(get_full_path_temp(), folder_name))

def get_all_urls_from_temp():
    return get_all_urls_from_file(URLSTEXTFILENAME)

def get_full_path_temp():
    return norm_path(os.path.join(str(os.getcwd()), TEMPFOLDERNAME))

def get_full_path_videos():
    return norm_path(os.path.join(get_full_path_temp(), VIDEOFOLDERNAME))

def get_dir_for_frames(video_file):
    dir_name = str(video_file).replace('.mp4', "")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

class FrameInfo:
    def __init__(self, fileName,sec, count):
        self.fileName = fileName
        self.sec = sec
        self.count = count

audioVideoTranslator = {".audio.ts": ".ts", ".m4a": ".mp4"}
class FileInfo:
    def __init__(self, fileName, audioName, videoName):
        self.fileName = fileName
        self.audioName = audioName
        self.videoName = videoName
