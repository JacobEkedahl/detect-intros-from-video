# ------------------------------------------------------------------------- #
# This will download a single video using svtplay-dl and then remove each   #                                                        
# frame beyond the provided timestamp (default 8 min). Will temporarily     #
# create a folder '/temp' for storing files during the work process.        #                                                
#                                                                           #
# Example usage:                                                            #        
#   py SimpleDownloader.py dl-vidoe-url -s -t 480                           #
#                                                                           # 
# Notice:                                                                   #
# 1. You can perform scene detection by flagging -scenedetect (-s)          #
# 3. You can modify cut off time by using -time (-t)                        # 
# ------------------------------------------------------------------------- #

import os
import sys 
import subprocess
from pathlib import Path

# Default cut off time for downloaded videos
DEFAULT_OPENING_LEN_SECONDS = 480

def get_first_video_file(directory):
    for filename in os.listdir(directory):
        if (".mp4") in filename:
            return filename
    return ""

# Downloads a video into a temp folder and returns the filename.
# Precondition no folder with the name '/temp' must exist    
def download_video(url, target_directory):
    os.mkdir('temp')
    parentDirectory = os.getcwd()
    directory = parentDirectory + "/temp"
    os.chdir(directory)
    p = subprocess.Popen("svtplay-dl " + url)
    p.wait()
    video_file = get_first_video_file(directory)
    os.chdir(parentDirectory)
    os.system("mv temp/* .")
    os.system("rm -r temp")
    return video_file

# Removes everything after the cut off point from the video
def extract_opening_from_video(video_file, cut_off_time_in_seconds):
    cmd = "ffmpeg -ss 0 -i %s -to %d -c copy opening.mp4" % (video_file, cut_off_time_in_seconds)
    p = subprocess.Popen(cmd)
    p.wait()
    os.remove(video_file)
    os.rename('opening.mp4', video_file)

# Addon for performing basic scene detection on the video 
def scene_detect(video_file):
    cmd = "python ./SceneDetector.py " + video_file
    p = subprocess.Popen(cmd)
    p.wait()


if __name__ == "__main__":

    if len(sys.argv) - 1 < 1:
        print("No arguments found")
        exit()

    cut_off_time_in_seconds = DEFAULT_OPENING_LEN_SECONDS
    doSceneDetect = False
    video_url = sys.argv[1]

    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "-s" or sys.argv[i] == "-scenedetect":
            doSceneDetect = True
        elif sys.argv[i] == "-t" and i + 1 < len(sys.argv):
            try: 
                cut_off_time_in_seconds = int(sys.argv[i + 1])
            except:
                print("Failed to convert %s into seconds " % sys.argv[i + 1])
                exit()
        elif sys.argv[i] == "-dir" and i + 1 < len(sys.argv):
            target_directory = sys.argv[i + 1]

    video_file = download_video(video_url, target_directory)
    print("download completed: %s" % video_file)

    if video_file != "":
        extract_opening_from_video(video_file, cut_off_time_in_seconds)
        if doSceneDetect: 
            print("Starting scene detection...")
            scene_detect(video_file)
    else:
        # if the download failed this folder should be empty
        os.system("rm temp")    
        print("Failed to download file.")
