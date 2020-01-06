from segmenter import simple_segmentor
from utils import file_handler, time_handler
from . import annotate as ann
from annotations.annotate import TimeInterval


def annotate_detected_scenes(segments, scenes, annotation):
    if len(segments) == 0 or len(scenes) == 0:
        return segments
    timestampsInSeconds = []
    for scene in scenes: 
        timestampsInSeconds.append(time_handler.to_seconds(scene['start']))
    segments = ann.set_presence_of_timestamps(annotation, segments, timestampsInSeconds, True)
    return segments
