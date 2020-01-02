import imageio_ffmpeg as ffmpeg
import subprocess
import logging 
import re
import os 
import json 

import db.video_repo as video_repo 
import utils.constants as constants
import utils.time_handler as time_handler
import utils.file_handler as file_handler

SEQUENCES_KEY = 'blackSequences'
SEQUENCE_KEY = 'blackSequence'
FRAMES_KEY = 'blackFrames'  
FRAME_KEY = 'blackFrame'
BLACK_KEY = 'black'
SAVE_TO_DB = constants.SAVE_TO_DB 
SAVE_TO_FILE = constants.SAVE_TO_FILE 
PRINT_OUTPUT = False 
THRESHOLD = constants.BLACK_DETECTOR_THRESHOLD
DURATION = constants.BLACK_DETECTOR_MIN_DUR 


def black_frames_to_timestamp_list(blackFrames):
    resultList = []
    for f in blackFrames:
        resultList.append(time_handler.to_seconds(f['time']))
    return resultList


def file_has_been_detected(video_file):
    if SAVE_TO_DB:
        try: 
            video = video_repo.find_by_file(os.path.basename(video_file))
            return (video is not None) and (SEQUENCES_KEY in video) and (FRAMES_KEY in video)
        except Exception as e: 
            logging.error(e)
    if SAVE_TO_FILE: 
        json_path = video_file.replace('.mp4', '') + '.json'
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                data = json.load(json_file)
                return (SEQUENCES_KEY in data) and (FRAMES_KEY in data)


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
                'start': time_handler.timestamp_to_str(float(data[0])*1000),
                'end': time_handler.timestamp_to_str(float(data[1])*1000),
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
        file_handler.save_to_file(video_file, SEQUENCES_KEY, blackSequences)
        file_handler.save_to_file(video_file, FRAMES_KEY, blackFrames)
    
    if SAVE_TO_DB: 
        try: 
            video_repo.set_data_by_file(os.path.basename(video_file), SEQUENCES_KEY, blackSequences)
            video_repo.set_data_by_file(os.path.basename(video_file), FRAMES_KEY, blackFrames)
        except Exception as e: 
            logging.error(e)

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
   