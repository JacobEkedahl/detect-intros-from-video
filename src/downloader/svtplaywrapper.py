import os
import pprint
import subprocess
import sys
from pathlib import Path

import numpy as np

# ---  will save videos in outputDir which is under under home directory ---

def downloadVideo(url, nameOfFolder):
    downloadPath = os.path.join(str(Path.home()), nameOfFolder)
    command = ["sh", "lib/runSvtPlay.sh", url, "--config", "lib/svtplay-dl.yaml", "--output", downloadPath]
    output = subprocess.call(command, shell=True) 
    # add step to mux and cut here
    print(output)

def downloadVideos(urls, nameOfFolder):
    downloadPath = os.path.join(str(Path.home()), nameOfFolder)
    command = ["sh", "lib/runSvtPlay.sh"] + urls + ["--config", "lib/svtplay-dl.yaml", "--output", downloadPath]
    output = subprocess.call(command, shell=True)
    print(output)

def startDownload(urls, nameOfFolder, numberOfEpisodes):
    numEpisodes = int(numberOfEpisodes)
    if (numEpisodes < 1):
        print("specify number of episodes")
        exit()
    if numEpisodes < len(urls):
        urls = urls[:-len(urls)+numEpisodes]
    downloadVideos(urls, nameOfFolder)

def start(nameOfTextFile, nameOfFolder, numberOfEpisodes):
    textFilePath = os.path.join(str(Path.home()), nameOfTextFile)
    urls = [line.rstrip('\n') for line in open(textFilePath)]
    startDownload(urls, nameOfFolder, numberOfEpisodes)
