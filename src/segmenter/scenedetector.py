# ------------------------------------------------------------------------- #
# Implements PySceneDetect to detect scene transitions of a video. Produces #
# a json file containing information about all detected scenes, as well as  #
# a cvs file containing a statistical analysis of all the frames.           #                                            
#                                                                           #
# Example usage 1:                                                          #        
#   py scenedetector.py myvideo.mp4                                         #
#                                                                           # 
# Example usage 2:                                                          # 
#   py scenedetector.py c:/users/home/videos                                #
#                                                                           #
# Notice:                                                                   #
# You can either provide a single .mp4 file or a directory. If a full path  # 
# to a directory is provided every single video will be processed           #
#                                                                           #
# ------------------------------------------------------------------------- #

# Source: https://pyscenedetect.readthedocs.io/en/latest/examples/usage-python/

import json
import os
import sys

import cv2
import numpy
import scenedetect
from scenedetect.detectors import ContentDetector, ThresholdDetector
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.scene_manager import SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.video_manager import VideoManager

import utils.constants as c
import db.video_repo as video_repo
import utils.time_handler as time_handler

DEFAULT_START_TIME      = 0.0        # 00:00:00.00
DEFAULT_END_TIME        = 600.0        # 00:10:00.00
DOWNSCALE_FACTOR        = c.DOWNSCALE_FACTOR
DATA_KEY                = 'sd_scenes'


def file_has_been_segmented(video_file):
    json_path = video_file.replace('.mp4', '') + '.json'
    if os.path.exists(json_path):
        with open(json_path) as json_file:
            data = json.load(json_file)
            return DATA_KEY in data
    else: 
        # in case json file does not exist we try the database
        video = video_repo.find_by_file(os.path.basename(video_file))
        return (video is not None) and (DATA_KEY in video)


def segment_video(video_file):
    # requires that they all have the same frame size, and optionally, framerate.

    if not os.path.exists(video_file):
        print("Error: %s does not exists." % video_file)
        return 

    try: 
        video_manager = VideoManager([video_file])
    except Exception as e: 
        print("Error: failed to read %s, data might be corrupted." % video_file)
        print(e)
        return 
    
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)

    contentDetector = ContentDetector()
    scene_manager.add_detector(contentDetector)
    threshholdDetector = ThresholdDetector()
    scene_manager.add_detector(threshholdDetector)
    base_timecode = video_manager.get_base_timecode()

    try:
        start_time = base_timecode + DEFAULT_START_TIME      
        end_time = base_timecode + DEFAULT_END_TIME   
        video_manager.set_duration(start_time=start_time, end_time=end_time)
        video_manager.set_downscale_factor(DOWNSCALE_FACTOR)
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list(base_timecode)

        json_path = video_file.replace('.mp4', '') + '.json'
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                data = json.load(json_file)
        else:
            data = { DATA_KEY: [] }
        for i, scene in enumerate(scene_list):
            start = scene[0].get_timecode()
            data[DATA_KEY].append({
                'start': start,
                'end':  scene[1].get_timecode(),
                'timestamp': time_handler.timestamp(start)
            })
        # Save
        video_repo.set_data_by_file(os.path.basename(video_file), DATA_KEY, data[DATA_KEY])
        with open(json_path, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)
        
        print("Scenedetector %s completed. " % video_file)
    
    except Exception as e: 
        print(e)
        
    finally:
        video_manager.release()

    
