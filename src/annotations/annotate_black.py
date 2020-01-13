import json

from segmenter import simple_segmentor
from utils import file_handler, time_handler
from . import annotate as ann
from annotations.annotate import TimeInterval

def annotate_black_sequences(segments, annotation, blackSequences):
    if len(segments) == 0 or len(blackSequences) == 0:
        return segments
    timeIntervals = []
    for seq in blackSequences:
        timeIntervals.append(TimeInterval(time_handler.seconds_to_str(seq['start']), time_handler.seconds_to_str(seq['end'])))
    for seg in segments:
        seg[annotation] = False 
    return ann.set_presence_of_time_interval_improved(annotation, segments, timeIntervals)
