import glob
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

TEMPFOLDERNAME = "gui/temp"
def get_all_unmerged_files():
    files = []
    types = ["*.audio.ts", "*.m4a"] #find audio files and match with videofiles

    for ext in types:
        audioExtNoStar = ext[1:]
        for audioName in Path(get_full_path_temp()).rglob(ext):
            audioName = str(audioName)
            videoName = audioName.replace(audioExtNoStar, audioVideoTranslator[audioExtNoStar], 1)
            fileName = audioName.replace(audioExtNoStar,  '', 1)
            files.append(FileInfo(fileName, audioName, videoName ))
    return files

def clear_temp():
    files = glob.glob(TEMPFOLDERNAME + '/*')
    for f in files:
        os.unlink(f)

def init_temp():
    if not os.path.exists(get_full_path_temp()):
        os.makedirs(get_full_path_temp())

audioVideoTranslator = {".audio.ts": ".ts", ".m4a": ".mp4"}
class FileInfo:
    def __init__(self, fileName, audioName, videoName):
        self.fileName = fileName
        self.audioName = audioName
        self.videoName = videoName

def get_full_path_temp():
    return os.path.join(str(os.getcwd()), TEMPFOLDERNAME)
