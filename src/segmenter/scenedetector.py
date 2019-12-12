# ------------------------------------------------------------------------- #
# Implements PySceneDetect to detect scene transitions of a video. Produces #
# a json file containing information about all detected scenes, as well as  #
# a cvs file containing a statistical analysis of all the frames.           #                                            
#                                                                           #
# Example usage:                                                            #        
#   py SceneDetector.py myvideo.mp4                                         #
#                                                                           # 
# ------------------------------------------------------------------------- #

# Source: https://pyscenedetect.readthedocs.io/en/latest/examples/usage-python/

import scenedetect 
import numpy
import cv2
import os 
import sys 
import json 

from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector


def main(video_file):

    # requires that they all have the same frame size, and optionally, framerate.
    video_manager = VideoManager([video_file])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    # Add ContentDetector algorithm (constructor takes detector options like threshold).
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    try:
        # Uses the video file path and replaces .mp4 with another ending
        stats_file_path = video_file.replace('.mp4', '') + '.stats.cvs'
        # If stats file exists, load it.
        if os.path.exists(stats_file_path):
            # Read stats from CSV file opened in read mode:
            with open(stats_file_path, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file, base_timecode)

        start_time = base_timecode + 20     # 00:00:00.00
        end_time = base_timecode + 600      # 00:10:00
        
        # Set video_manager duration to read frames from [start_time] to [end_time].
        video_manager.set_duration(start_time=start_time, end_time=end_time)

        # Set downscale factor to improve processing speed (no args means default).
        video_manager.set_downscale_factor()

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)
        # Like FrameTimecodes, each scene in the scene_list can be sorted if the
        # list of scenes becomes unsorted.

        print('List of scenes obtained:')

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

        # We only write to the stats file if a save is required:
        if stats_manager.is_save_required():
            with open(stats_file_path, 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)

    finally:
        video_manager.release()


if len(sys.argv) - 1 < 1:
    print("No arguments found")
    exit()
if (".mp4") in sys.argv[1]: 
    main(sys.argv[1])
else:
    print("Invalid videofile")
