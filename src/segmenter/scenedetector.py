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
from scenedetect.detectors import ContentDetector
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.scene_manager import SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.video_manager import VideoManager

import utils.file_handler as file_handler

DEFAULT_START_TIME = 0.0        # 00:00:00.00
DEFAULT_END_TIME = 600.0        # 00:10:00.00

def segment_all_videos():
    video_files = file_handler.get_all_mp4_files()
    i = 1
    max = len(video_files)
    for file in video_files:
        segment_video(str(file))
        print("segmented %d/%d" % (i, max))
        i = i + 1

def segment_video(video_file):
    # requires that they all have the same frame size, and optionally, framerate.
    video_manager = VideoManager([video_file])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    # Add ContentDetector algorithm (constructor takes detector options like threshold).
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    try:
        stats_file_path = video_file.replace('.mp4', '') + '.stats.cvs'
        if os.path.exists(stats_file_path):
            with open(stats_file_path, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file, base_timecode)

        start_time = base_timecode + DEFAULT_START_TIME      
        end_time = base_timecode + DEFAULT_END_TIME   
        video_manager.set_duration(start_time=start_time, end_time=end_time)
        video_manager.set_downscale_factor(10)
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list(base_timecode)
        print('List of scenes obtained from %s:' % video_file)

        json_data = {}
        json_data['scenes'] = []

        for i, scene in enumerate(scene_list):
            json_data['scenes'].append({
                'scene': i + 1,
                'start': scene[0].get_timecode(),
                'startFrame': scene[0].get_frames(),
                'end':  scene[1].get_timecode(),
                'endFrame': scene[1].get_frames(),
                'intro': False
            })
            print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i+1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),))

        with open(video_file.replace('.mp4', '') + '.json', 'w') as outfile:
            json.dump(json_data, outfile)

        if stats_manager.is_save_required():
            with open(stats_file_path, 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)

    finally:
        video_manager.release()
