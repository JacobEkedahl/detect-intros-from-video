# 
# Merges the subtitle files with the scene annotation file                                                  

# Example usage 1:                                                                 
#   py annotate_subtitles.py --subs subtitles.srt annotationfile.json -print
# 
# Note: print is optional                                                  
#         

import json
import os

from classifier import prob_calculator
from utils import file_handler, srt_to_json, time_handler

from . import scene_annotation
from .annotate import TimeInterval, set_presence_of_time_interval_improved


def annotate_subs_from_video(video_file):
    srt_file = file_handler.get_srt_from_video(video_file)
    if os.path.exists(srt_file):
        seg_file = file_handler.get_seg_file_from_video(video_file)
        annotate_srt_on_scenes(srt_file, seg_file, video_file)

# Creates a annotation in the segmentation file for presence of subtitles in particular scenes
#

def get_longest_sub(avg_intro_size, subtitles):
    result = []
    current_seq = {}
    start_time = 0

    for sub_i in range(len(subtitles)):
        subs = subtitles[sub_i]
        start = time_handler.timestamp(subs['start']) / 1000
        diff = 0
        prev_time = 0
        if sub_i == 0 or start != 0:
            if start_time != 0:
                prev_time = time_handler.timestamp(subtitles[sub_i - 1]['end']) / 1000
            else:
                start_time = 1

        diff = start - prev_time
        if diff < 120 and diff > 20: #120 sec long limit
            if abs(avg_intro_size - diff) > 10:
                if prev_time + avg_intro_size < 480:
                    entry = {"start": time_handler.timestamp_to_str(prev_time * 1000), "end": time_handler.timestamp_to_str((prev_time + avg_intro_size) * 1000)}
                    result.append(entry)
                if prev_time - avg_intro_size > 0:
                    result.append({"start": time_handler.timestamp_to_str((prev_time - avg_intro_size) * 1000), "end": time_handler.timestamp_to_str(start * 1000)})
                else:
                    result.append({"start": time_handler.timestamp_to_str(0), "end": time_handler.timestamp_to_str(avg_intro_size * 1000)})
            else:
                result.append({"start": time_handler.timestamp_to_str(prev_time * 1000), "end": time_handler.timestamp_to_str(start * 1000)})
           # print(current_seq)
    if 'start' in current_seq:
        result.append(current_seq)
    return result

def clean_subs(subtitles):
    new_subs = []
    for subs in subtitles:
        if time_handler.timestamp(subs["start"]) > 300000: #only keep subs until 5 min
            break
        new_subs.append(subs)
    return new_subs

def annotate_srt_on_scenes(srtFile, segmentationFile, video_file):
    srt_str = open(srtFile, 'r').read()
    parsed_srt = srt_to_json .parse_srt(srt_str)
    if len(parsed_srt) <= 30:
        print("this sub file is too short to use for annotation")
        #scene_annotation.delete_annotation('subtitles', segmentationFile)
        return
    parsed_srt = clean_subs(parsed_srt)
    subtitleTimeIntervals = []
    avg_size = prob_calculator.get_most_probable_size(video_file)
    longest_sub = get_longest_sub(avg_size, parsed_srt)
    other_videos = file_handler.get_all_other_videos_in_series(video_file)
    other_intros = file_handler.get_intros_from_videos(other_videos)
    longest_sub = prob_calculator.get_the_most_likely_sequence(longest_sub, other_intros)
    for subtitle in longest_sub:
        print("sub title: " + str(subtitle) + " - " + str(segmentationFile))
        timeInterval = TimeInterval(subtitle['start'], subtitle['end'])
        subtitleTimeIntervals.append(timeInterval)
    with open(segmentationFile) as json_file:
        data = json.load(json_file)
        for scene in data['scenes']:
            scene['subtitles'] = False
        set_presence_of_time_interval_improved('subtitles', data['scenes'], subtitleTimeIntervals)
        with open(segmentationFile, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)
