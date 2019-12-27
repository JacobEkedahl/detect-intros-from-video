# 
# Merges the subtitle files with the scene annotation file                                                  

# Example usage 1:                                                                 
#   py annotate_subtitles.py --subs subtitles.srt annotationfile.json -print
# 
# Note: print is optional                                                  
#         

import json
import os

from utils import file_handler, srt_to_json

from .annotate import TimeInterval, set_presence_of_time_interval


def annotate_subs_from_video(video_file):
    srt_file = file_handler.get_srt_from_video(video_file)
    if os.path.exists(srt_file):
        seg_file = file_handler.get_seg_file_from_video(video_file)
        annotate_srt_on_scenes(srt_file, seg_file)

# Creates a annotation in the segmentation file for presence of subtitles in particular scenes
#
def annotate_srt_on_scenes(srtFile, segmentationFile):
    srt_str = open(srtFile, 'r').read()
    parsed_srt = srt_to_json .parse_srt(srt_str)
    subtitleTimeIntervals = []
    for subtitle in parsed_srt:
        timeInterval = TimeInterval(subtitle['start'], subtitle['end'])
        subtitleTimeIntervals.append(timeInterval)
    with open(segmentationFile) as json_file:
        data = json.load(json_file)
        for scene in data['scenes']:
            scene['subtitles'] = False
        set_presence_of_time_interval('subtitles', data['scenes'], subtitleTimeIntervals)
        with open(segmentationFile, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)


def execute(argv):
    if len(argv) - 1 <= 2:
        print("Error: Need to provide (2) srt file and (3) segment file.")
        return
    subtitlesFile = argv[2]
    segmentFile = argv[3]
    annotate_srt_on_scenes(subtitlesFile, segmentFile)
    for i in range(1, len(argv)):
        if (argv[i] == "-print"):
            with open(segmentFile) as json_file:
                data = json.load(json_file)
                for scene in data['scenes']:
                    print(scene)
