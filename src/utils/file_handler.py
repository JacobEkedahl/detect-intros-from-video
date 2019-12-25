import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from . import constants as c

TEMPFOLDERNAME = "temp"
VIDEOFOLDERNAME = "videos"
URLSTEXTFILENAME = "video-serier.txt"

def create_folderstructure_if_not_exists():
    if not os.path.exists(get_full_path_videos()):
        os.makedirs(get_full_path_videos())

def get_all_other_videos_in_series(video_file):
    parent_dir = os.path.dirname(video_file)
    other_videos = get_all_files_by_type(parent_dir, 'mp4')
    other_videos.remove(str(video_file))
    return other_videos

def get_all_urls_from_file(file_name):
    text_file_path = os.path.join(get_full_path_temp(), file_name)
    urls = [line.rstrip('\n') for line in open(text_file_path)]
    return [item for item in urls if item.startswith("http")]

def get_seg_file_from_video(video_file):
    return str(video_file).replace('.mp4', '.json')

def get_all_files_by_type(path, fileType):
    files = []
    for filename in Path(path).rglob('*.' + fileType):
        files.append(str(filename))
    return files

def get_all_mp4_files():
    return get_all_files_by_type(get_full_path_videos(), 'mp4')

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

def does_meta_contain_obj(obj_type, video_file):
    dir = get_dir_for_meta(video_file)
    return os.path.isfile(os.path.join(dir, obj_type))

# Helper functions
def get_full_path_folder(folder_name):
    return os.path.join(get_full_path_temp(), folder_name)

def get_all_urls_from_temp():
    return get_all_urls_from_file(URLSTEXTFILENAME)

def get_full_path_temp():
    return os.path.join(str(os.getcwd()), TEMPFOLDERNAME)

def get_full_path_videos():
    return os.path.join(get_full_path_temp(), VIDEOFOLDERNAME)

def get_dir_for_meta(video_file):
    return get_dir_by_type(video_file, "-meta")

def get_dir_by_type(video_file, ext_type):
    dir_name = str(video_file).replace('-converted.mp4', ext_type)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

audioVideoTranslator = {".audio.ts": ".ts", ".m4a": ".mp4"}
class FileInfo:
    def __init__(self, fileName, audioName, videoName):
        self.fileName = fileName
        self.audioName = audioName
        self.videoName = videoName
