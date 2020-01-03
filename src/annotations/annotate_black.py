import json

from segmenter import simple_segmentor
from utils import file_handler, time_handler
from . import annotate as ann
from annotations.annotate import TimeInterval


def annotate_black_frames(segments, annotation, blackFrames):
    if len(segments) == 0:
        return segments
    timestampsInSeconds = []
    for f in blackFrames: 
        timestampsInSeconds.append(time_handler.to_seconds(f['time']))
    segments = ann.set_presence_of_timestamps(annotation, segments, timestampsInSeconds, True)
    return segments


def annotate_black_sequences(segments, annotation, blackSequences):
    if len(segments) == 0 or len(blackSequences) == 0:
        return segments
    timeIntervals = []
    for seq in blackSequences:
        timeIntervals.append(TimeInterval(seq['start'], seq['end']))
    for seg in segments:
        seg[annotation] = False 
    return ann.set_presence_of_time_interval_improved(annotation, segments, timeIntervals)

# This will replace the black frame and sequence annotations with a new combined key 
def combine_annotation_into(segments, annotation, blakcSequencKey, blackFrameKey, removeOld):
    for seg in segments: 
        if seg[blakcSequencKey] or seg[blackFrameKey]: 
            seg[annotation] = True
        else:
            seg[annotation] = False 
        if removeOld:
            seg.pop(blakcSequencKey)
            seg.pop(blackFrameKey)
    return segments 
