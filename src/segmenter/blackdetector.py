import imageio_ffmpeg as ffmpeg
import subprocess
import logging 
import re
import os 
import json 
 
import utils.constants as constants
import utils.time_handler as time_handler
import utils.file_handler as file_handler

SEQUENCES_KEY = 'blackSequences'
SEQUENCE_KEY = 'blackSequence'
FRAMES_KEY = 'blackFrames'  
FRAME_KEY = 'blackFrame'
BLACK_KEY = 'black'
SAVE_TO_FILE = False 
PRINT_OUTPUT = False 
THRESHOLD = constants.BLACK_DETECTOR_THRESHOLD
DURATION = constants.BLACK_DETECTOR_MIN_DUR 


def black_frames_to_timestamp_list(blackFrames):
    resultList = []
    for f in blackFrames:
        resultList.append(time_handler.to_seconds(f['time']))
    return resultList


def file_has_been_detected(video_file):
    if SAVE_TO_FILE: 
        data = file_handler.load_from_video_file(video_file)
        return (SEQUENCES_KEY in data) and (FRAMES_KEY in data)
    return False 


def detect_blackness(video_file):
    
    cmd = ( "%s -i %s -vf blackdetect=d=%f:pix_th=%f -an -f null -y /dev/null" % (ffmpeg._utils.get_ffmpeg_exe(), video_file, DURATION, THRESHOLD) ).split(" ")
    output = subprocess.Popen( cmd, stderr=subprocess.PIPE ).communicate()[1]

    blackFrames = []
    blackSequences = []

    for line in output.decode('utf-8').splitlines():
        if "blackdetect" in line:
            # Line = [blackdetect @ 03e7e280] black_start:0 black_end:4.24 black_duration:4.24
            data = re.findall(r"[-+]?\d*\.?\d+|\d+", line.split("]")[1]) 
            blackSequences.append({ 
                'start': float(data[0]),
                'end': float(data[1]),
            })
        elif "frame=" in line: 
            # frame=12001 fps=420 q=-0.0 Lsize=N/A time=00:08:00.04 bitrate=N/A speed=16.8x
            time = line.split("time=")[1].split(" bitrate=")[0]
            frame = line.split("frame=")[1].split(" fps=")[0]
            blackFrames.append({
                'frame': int(frame),
                'time': time
            })   
        
    if SAVE_TO_FILE: 
        file_handler.save_to_video_file(video_file, SEQUENCES_KEY, blackSequences)
        file_handler.save_to_video_file(video_file, FRAMES_KEY, blackFrames)
    
    if PRINT_OUTPUT: 
        if len(blackSequences) > 0:
            print("sequences: ")
            for seq in blackSequences: 
                print(seq)
        if len(blackFrames) > 0:
            print("frames: ")
            for f in blackFrames: 
                print(f)

    print("Blackdetection of %s completed (%d sequences, %d frames) " % (video_file, len(blackSequences), len(blackFrames)))
    
    return blackSequences, blackFrames
   