import json
import os 

from moviepy.editor import VideoFileClip
from utils import constants, time_handler

SCENE_KEY = 'scenes'

def segment_video_with_url(video_file, url):
    print("video_file: " + video_file)
    try:
        clip = VideoFileClip(str(video_file))
        video_length = int(clip.duration * 1000)
        step_length = int(constants.SEGMENT_LENGTH * 1000)

        json_path = video_file.replace('.mp4', '') + '.json'
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                data = json.load(json_file)
        else:
            data = {}

        scene_index = 0
        data['url'] = url
        data[SCENE_KEY] = []

        for scene in range(0, video_length, step_length):
            start = time_handler.timestamp_to_str(scene)
            end = time_handler.timestamp_to_str(scene + step_length)
            data[SCENE_KEY].append({
                'scene': scene_index,
                'start': start,
                'end':  end
            })
            scene_index += 1
        with open(json_path) as outfile:
            json.dump(data, outfile)
    except Exception as e:
        print(e)
    
def segment_video(video_file):
    print("video_file: " + video_file)
    try:
        clip = VideoFileClip(str(video_file))
        video_length = int(clip.duration * 1000)
        step_length = int(constants.SEGMENT_LENGTH * 1000)

        json_path = video_file.replace('.mp4', '') + '.json'
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                data = json.load(json_file)
        else:
            data = {}

        scene_index = 0
        data[SCENE_KEY] = []
        
        for scene in range(0, video_length, step_length):
            start = time_handler.timestamp_to_str(scene)
            end = time_handler.timestamp_to_str(scene + step_length)
            data['scenes'].append({
                'scene': scene_index,
                'start': start,
                'end':  end
            })
            scene_index += 1
        with open(video_file.replace('.mp4', '') + '.json', 'w') as outfile:
            json.dump(data, outfile)
    except Exception as e:
        print(e)
