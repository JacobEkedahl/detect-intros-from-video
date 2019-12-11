import os
import re
import subprocess
from glob import glob

import imageio_ffmpeg as ffmpeg

audioVideoTranslator = {".audio.ts": ".ts", ".m4a": ".mp4"}

def mergeImageAndAudio(fullPath):
    files = getAllPaths(fullPath)
    for file in files:
        print(file.audioName + " : " + file.videoName)
        output = file.fileName + ".mkv"
        command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", file.audioName, "-i", file.videoName, "-c", "copy", "-t", "00:10:00.0", "-y", output]
        output = subprocess.call(command, shell=True) 
        os.remove(file.audioName)
        os.remove(file.videoName)

def getAllPaths(fullPath):
    files = []
    types = ["*.audio.ts", "*.m4a"] #find audio files and match with videofiles
    for dir,_,_ in os.walk(fullPath):
        for ext in types:
            allAudioPaths = glob(os.path.join(dir,ext))
            if not allAudioPaths:
                continue
            
            audioExtNoStar = ext[1:]
            for audioName in allAudioPaths:
                videoName = audioName.replace(audioExtNoStar,  audioVideoTranslator[audioExtNoStar], 1)
                fileName = audioName.replace(audioExtNoStar,  '', 1)
                files.append(FileInfo(fileName, audioName, videoName ))
    return files

class FileInfo:
    def __init__(self, fileName, audioName, videoName):
        self.fileName = fileName
        self.audioName = audioName
        self.videoName = videoName
