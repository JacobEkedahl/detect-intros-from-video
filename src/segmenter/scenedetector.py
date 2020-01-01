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
SAVE_TO_DB = True
SAVE_TO_FILE = True 
PRINT_OUTPUT = False 


def file_has_been_segmented(video_file):
    if SAVE_TO_DB:
        try: 
            video = video_repo.find_by_file(os.path.basename(video_file))
            return (video is not None) and (DATA_KEY in video)
        except Exception as e: 
            print(e)
    if SAVE_TO_FILE: 
        json_path = video_file.replace('.mp4', '') + '.json'
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                data = json.load(json_file)
                return DATA_KEY in data


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

        scenes = []
        for scene in scene_list: 
            start =  scene[0].get_timecode()
            end = scene[1].get_timecode()
            scenes.append({
                'start': start,
                'end': end, 
                'timestamp': time_handler.to_seconds(start)
            })

        if SAVE_TO_FILE:  
            data = {}
            json_path = video_file.replace('.mp4', '') + '.json'
            if os.path.exists(json_path):
                with open(json_path) as json_file:
                    data = json.load(json_file)
            data[DATA_KEY] = scenes           
            with open(json_path, 'w') as outfile:
                json.dump(data, outfile, indent=4, sort_keys=False)

        if SAVE_TO_DB: 
            try: 
                video_repo.set_data_by_file(os.path.basename(video_file), DATA_KEY, data[DATA_KEY])
            except Exception as e: 
                print(e)
        
        if PRINT_OUTPUT:
            for scene in scenes: 
                print(scene)

        print("Scenedetector %s completed. " % video_file)
    
    except Exception as e: 
        print(e)
        
    finally:
        video_manager.release()

    return scenes 

    
