import json
import os
import sys as s
from pathlib import Path

import numpy as np

from segmenter import simple_segmentor

from . import file_handler, time_handler

NO_RESULT = ""

DATAFOLDERNAME = "data"
ANNOTATIONS = "dataset.json"

def create_video_serier_file(force):
    intros = get_intros_from_data()
    video_serier_file = file_handler.get_video_serie_file()
    if force is False:
        all_videos = file_handler.get_all_mp4_files()
        for video_file in all_videos:
            url = file_handler.get_url_from_file_name(video_file)
            intros = [i for i in intros if not (i['url'] == url)] 
    with open(video_serier_file, 'w') as f:
        for intro in intros:
            f.write("%s\n" % intro["url"])

# should only be used when creating the dataset, to fetch the actual intros, use get_all_intros
def get_intros_from_data():
    intro_file = get_full_path_intros()
    with open(intro_file) as json_file:
        data = json.load(json_file)
        return data['intro']

def print_urls():
    intros = get_intros_from_data()
    for intro in intros:
        print(intro["url"])

def get_intros_from_videos(video_files):
    result = []
    for video_file in video_files:
        intro = get_intro_from_video(video_file)
        if intro is not None:
            result.append(intro)
    if len(result) > 0:
        return result
    return None

def get_intro_from_video(video_file):
    seg_file = file_handler.get_seg_file_from_video(video_file)
    scenes = None
    intro = {"start": None, "end": None}
    with open(seg_file) as json_file:
        data = json.load(json_file)
        scenes = data['scenes']
        if 'intro' in scenes[0]:
            for scene in scenes:
                if scene["intro"] is True:
                    if intro["start"] is not None:
                        start = time_handler.timestamp(scene["start"]) / 1000
                        intro["end"] = start
                    else:
                        intro["start"] = int(time_handler.timestamp(scene["start"])) / 1000 
                elif intro["start"] is not None and intro["end"] is not None:
                    return intro
    return None

# Given a root directory it finds all json files and extract all intros annotated
# Stores this data inside intro.json under output directory 
def extract_intros(path, output):
    files = []
    types = ["*.json"] 

    for ext in types:
        for file in Path(path).rglob(ext):
            fileWithNoDir = os.path.basename(file)
            print(str(fileWithNoDir))
            filePath = str(file)
            with open(filePath) as json_file:
                data = json.load(json_file)
                if "intro" in data:
                    intro = data["intro"]
                    files.append({"url": fileWithNoDir, "start": intro["start"], "end": intro["end"]})
                else:
                    files.append({"url": fileWithNoDir, "start": NO_RESULT, "end": NO_RESULT})

    result = {"intro": files}
    with open(os.path.join(output, 'intros' + '.json') , 'w') as outfile:
        json.dump(result, outfile)

def get_full_path_data():
    return os.path.join(str(os.getcwd()), DATAFOLDERNAME)

def get_full_path_intros():
    return os.path.join(str(get_full_path_data()), ANNOTATIONS)

if __name__ == "__main__":
    extract_intros(s.argv[1], s.argv[2])
