import json
import logging
import os

from moviepy.editor import VideoFileClip
from utils import constants, file_handler, time_handler

SCENES_KEY = 'scenes'

SAVE_TO_FILE = constants.SAVE_TO_FILE

def file_has_been_segmented(video_file):
    data = file_handler.load_from_video_file(video_file)
    return SCENES_KEY in data


def get_video_segments(video_file):
    if file_has_been_segmented(video_file):
        data = file_handler.load_from_video_file(video_file)
        return data[SCENES_KEY]
    else: 
        return segment_video(video_file)


#TODO: Remove 
def segment_video_with_url(video_file, url):
    file_handler.save_to_video_file(video_file, "url", url)
    return segment_video(video_file) 


def segment_video(video_file):
    try:
        clip = VideoFileClip(str(video_file))
        video_length = int(clip.duration * 1000)
        step_length = int(constants.SEGMENT_LENGTH * 1000)
        clip.close()
        scene_index = 0
        segments = []
        for scene in range(0, video_length, step_length):
            start = time_handler.timestamp_to_str(scene)
            end = time_handler.timestamp_to_str(scene + step_length)
            segments.append({
                'scene': scene_index,
                'start': start,
                'end':  end
            })
            scene_index += 1

        if SAVE_TO_FILE:
            file_handler.save_to_video_file(video_file, SCENES_KEY, segments)
    
        return segments

    except Exception as e:
        logging.exception(e)
