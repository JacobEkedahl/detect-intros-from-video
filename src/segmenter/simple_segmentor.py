import json

from moviepy.editor import VideoFileClip
from utils import constants, time_handler


def segment_video(video_file):
    print("video_file: " + video_file)
#try:
    clip = VideoFileClip(video_file)
    video_length = int(clip.duration * 1000)
    step_length = int(constants.SEGMENT_LENGTH * 1000)

    json_data = {}
    scene_index = 0
    json_data['scenes'] = []

    for scene in range(0, video_length, step_length):
        start = time_handler.timestamp_to_str(scene)
        end = time_handler.timestamp_to_str(scene + step_length)
        json_data['scenes'].append({
            'scene': scene_index,
            'start': start,
            'end':  end,
            'intro': False
        })
        scene_index += 1
    with open(video_file.replace('.mp4', '') + '.json', 'w') as outfile:
        json.dump(json_data, outfile)
   # except Exception as e:
    #    print(e)
