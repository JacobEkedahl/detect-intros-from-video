import os
import re
import subprocess
from glob import glob

import imageio_ffmpeg as ffmpeg

from segmenter import scenedetector

audioVideoTranslator = {".audio.ts": ".ts", ".m4a": ".mp4"}

def mergeImageAndAudio(fullPath):
    files = getAllPaths(fullPath)
    for file in files:
        print(file.audioName + " : " + file.videoName)
        output = file.fileName + "-converted.mp4"
        command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", file.audioName, "-i", file.videoName, "-c", "copy", "-t", "00:08:00.0", "-y", output]
        subprocess.call(command, shell=True) 
        os.remove(file.audioName)
        os.remove(file.videoName)
        scenedetector.segment_video(output)

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
