import json

from segmenter import simple_segmentor
from utils import file_handler, time_handler

from . import annotate as ann
from .annotate import TimeInterval


def annotate_intro(video_file, url):
    print("intro annotated")
    intros = file_handler.get_intros()
    seq = {}
    intro = next((sub for sub in intros if sub['url'] == url), None) 
    if intro is not None:
        if time_handler.timestamp(intro["start"]) == 0 and time_handler.timestamp(intro["end"]) == 0:
            intro = None
        else:
            seq = {"start": intro["start"], "end": intro["end"]}
    if 'start' not in seq:
        print("could not find any intro to annotate with")
        return
        
    segmentationFile = file_handler.get_seg_file_from_video(video_file)
    scenes = None
    timeIntervals = []

    with open(segmentationFile) as json_file:
        data = json.load(json_file)
        scenes = data['scenes']
        for scene in scenes:
            scene['intro'] = False
        timeIntervals.append(TimeInterval(seq["start"], seq["end"]))
        ann.set_presence_of_time_interval_improved('intro', data['scenes'], timeIntervals)
        data['scenes'] = scenes
        with open(segmentationFile, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)
