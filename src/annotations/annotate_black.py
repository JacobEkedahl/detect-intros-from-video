import json

from segmenter import simple_segmentor
from utils import file_handler, time_handler
from . import annotate as ann
from annotations.annotate import TimeInterval


def annotate_black_frames(segments, annotation, blackFrames):
    if len(segments) == 0:
        return
    timestampsInSeconds = []
    for f in blackFrames: 
        timestampsInSeconds.append(time_handler.str_to_seconds(f['time']))
    segments = ann.set_presence_of_timestamps(annotation, segments, timestampsInSeconds, True)


def annotate_black_sequences(segments, annotation, blackSequences):
    if len(segments) == 0 or len(blackSequences) == 0:
        return segments
    timeIntervals = []
    for seq in blackSequences:
        timeIntervals.append(TimeInterval(time_handler.seconds_to_str(seq['start']), time_handler.seconds_to_str(seq['end'])))
    for seg in segments:
        seg[annotation] = False 
    return ann.set_presence_of_time_interval_improved(annotation, segments, timeIntervals)

# This will combine annotations of black frames and black sequences into one, if removeOld=True then the separate annotations will be removed.
def combine_annotation_into(segments, annotation, blackSequencKey, blackSequences, blackFrameKey, blackFrames, removeOld):
    if (len(segments) > 0 and (len(blackSequences) > 0 or len(blackFrames) > 0)):
        for seg in segments: 
            if (blackSequencKey in seg and seg[blackSequencKey]) or (blackFrameKey in seg and seg[blackFrameKey]):
                seg[annotation] = True
            else:
                seg[annotation] = False 
            if removeOld:
                if blackFrameKey in seg: 
                    seg.pop(blackFrameKey)
                if blackSequencKey in seg: 
                    seg.pop(blackSequencKey)

