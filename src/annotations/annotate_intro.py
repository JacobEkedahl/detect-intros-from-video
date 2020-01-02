import json
import os

from segmenter import simple_segmentor
from stats import prob_calculator
from utils import extractor, file_handler, time_handler

from . import annotate as ann
from .annotate import TimeInterval


def annotate_intro(video_file, seq):
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

def annotate_intro_from_url(video_file, url):
    print("intro annotated")
    intros = extractor.get_intros_from_data()
    seq = {}
    intro = next((sub for sub in intros if sub['url'] == url), None) 
    if intro is not None:
        start = time_handler.timestamp(intro["start"])
        end = time_handler.timestamp(intro["end"])
        if not (start == 0 and end == 0): # is it an actual intro
            seq = {"start": intro["start"], "end": intro["end"]}
    if 'start' not in seq:
        print("could not find any intro to annotate with")
        return

    annotate_intro(video_file, seq)
