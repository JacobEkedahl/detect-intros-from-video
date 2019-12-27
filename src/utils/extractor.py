import json
import os
import sys as s
from pathlib import Path

import numpy as np

from . import file_handler, time_handler

NO_RESULT = ""

def print_urls():
    intros = file_handler.get_intros()
    for intro in intros:
        print(intro["url"])

def get_intro_from_video(video_file):
    seg_file = file_handler.get_seg_file_from_video(video_file)
    scenes = None
    intro = {"start": None, "end": None}
    with open(seg_file) as json_file:
        data = json.load(json_file)
        scenes = data['scenes']
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



if __name__ == "__main__":
    extract_intros(s.argv[1], s.argv[2])
