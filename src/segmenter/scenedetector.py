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
import logging 

import cv2
import numpy
import scenedetect
from scenedetect.detectors import ContentDetector, ThresholdDetector
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.scene_manager import SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.video_manager import VideoManager

import utils.constants as constants
import db.video_repo as video_repo
import utils.time_handler as time_handler
import utils.constants as constants 
import utils.file_handler as file_handler

DEFAULT_START_TIME      = 0.0        # 00:00:00.30
DEFAULT_END_TIME        = constants.VIDEO_START_LEN + 0.30
DOWNSCALE_FACTOR        = constants.DOWNSCALE_FACTOR
DATA_KEY                = 'sd_scenes'
SAVE_TO_DB = False 
SAVE_TO_FILE = constants.SAVE_TO_FILE 
PRINT_OUTPUT = False 


def file_has_been_segmented(video_file):
    if SAVE_TO_DB:
        try: 
            video = video_repo.find_by_file(os.path.basename(video_file))
            return (video is not None) and (DATA_KEY in video)
        except Exception as e: 
            logging.exception(e)
    if SAVE_TO_FILE: 
        data = file_handler.load_from_video_file(video_file)
        return DATA_KEY in data


def detect_scenes(video_file):
    # requires that they all have the same frame size, and optionally, framerate.
    if not os.path.exists(video_file):
        logging.warning("%s does not exists.", video_file)
        return 
    try: 
        video_manager = VideoManager([video_file])
    except Exception as e: 
        logging.error("Error: failed to read %s, data might be corrupted.", video_file)
        logging.exception(e)
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
        end_time = base_timecode + float(DEFAULT_END_TIME)
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
            })

        if SAVE_TO_FILE:  
            file_handler.save_to_video_file(video_file, DATA_KEY, scenes)
        if SAVE_TO_DB: 
            try: 
                video_repo.set_data_by_file(os.path.basename(video_file), DATA_KEY, scenes)
            except Exception as e: 
                logging.exception(e)
        if PRINT_OUTPUT:
            for scene in scenes: 
                print(scene)

        print("Scenedetector %s completed. " % video_file)
    
        return scenes 

    except Exception as e: 
        logging.exception(e)

    finally:
        video_manager.release()


    
