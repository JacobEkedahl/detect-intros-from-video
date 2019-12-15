import os
from pathlib import Path

from . import constants as c


def norm_path(full_path):
    return os.path.normpath(full_path)

def create_folderstructure_if_not_exists():
    ##scrape svt and fetch urls, save in temp
    if not os.path.exists(get_full_path_videos()):
        os.makedirs(get_full_path_videos())

def get_full_path_videos():
    return norm_path(os.path.join(get_full_path_temp(), c.VIDEOFOLDERNAME))

def get_full_path_temp():
    return norm_path(os.path.join(str(os.getcwd()), c.TEMPFOLDERNAME))

def get_full_path_folder(folder_name):
    return norm_path(os.path.join(get_full_path_temp(), folder_name))

def get_all_urls_from_temp():
    return get_all_urls_from_file(c.URLSTEXTFILENAME)

def get_all_urls_from_file(file_name):
    text_file_path = norm_path(os.path.join(get_full_path_temp(), file_name))
    urls = [line.rstrip('\n') for line in open(text_file_path)]
    return [item for item in urls if item.startswith("http")]

def get_all_mp4_files():
    files = []
    for filename in Path(get_full_path_videos()).rglob('*.mp4'):
        print(filename)
        files.append(filename)
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


audioVideoTranslator = {".audio.ts": ".ts", ".m4a": ".mp4"}
class FileInfo:
    def __init__(self, fileName, audioName, videoName):
        self.fileName = fileName
        self.audioName = audioName
        self.videoName = videoName
