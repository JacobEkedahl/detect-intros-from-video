import json

from utils import file_handler, simple_segmentor, time_handler

from . import annotate as ann
from .annotate import TimeInterval


## function for annotating sequences of matched frames
def annotate_meta_data(sequences, description, video_file):
    if len(sequences) == 0: ## perhaps remove annotations of this type
        return
    print(description + " is annotating")
    timeIntervals = []
    data = file_handler.load_from_video_file(video_file)
    scenes = data["scenes"]
    for scene in scenes:
        scene[description] = False
    for seq in sequences:
        print(seq)
        start = time_handler.timestamp_to_str(seq["start"] * 1000)
        end = time_handler.timestamp_to_str(seq["end"] * 1000)
        timeIntervals.append(TimeInterval(start, end))
        ann.set_presence_of_time_interval_improved(description, data['scenes'], timeIntervals)
    file_handler.save_to_video_file(video_file, "scenes", scenes)
    return scenes 
