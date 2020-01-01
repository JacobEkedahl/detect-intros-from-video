import json

from segmenter import simple_segmentor
from utils import file_handler, time_handler

from . import annotate as ann
from .annotate import TimeInterval


## function for annotating sequences (pitches and matched frames)
def annotate_meta_data(sequences, description, video_file):
    if len(sequences) == 0: ## perhaps remove annotations of this type
        return
    print(description + " is annotating")
    timeIntervals = []
    segmentationFile = file_handler.get_seg_file_from_video(video_file)
    scenes = None
    with open(segmentationFile) as json_file:
        data = json.load(json_file)
        scenes = data['scenes']
        for scene in scenes:
            scene[description] = False

        for seq in sequences:
            print(seq)
            start = time_handler.timestamp_to_str(seq["start"] * 1000)
            end = time_handler.timestamp_to_str(seq["end"] * 1000)
            timeIntervals.append(TimeInterval(start, end))
            ann.set_presence_of_time_interval_improved(description, data['scenes'], timeIntervals)
        data['scenes'] = scenes
        with open(segmentationFile, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)