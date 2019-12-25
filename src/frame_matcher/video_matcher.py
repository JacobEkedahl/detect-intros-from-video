
# ------------------------------------------------------------------------- #
# Find matches between two videos, each video represented by its fullpath   #
# The result is a list of number of matches with a timestamp in seconds     #
# The algorithm used is called hashing                                      #

import imagehash
from PIL import Image

import annotations.annotate as ann
import utils.constants as c
import utils.file_handler as file_handler
from annotations.annotate import TimeInterval
from utils import object_handler as handler

from . import frame_comparer as comparer


def print_pitches(file_A):
    print("pitches: ")
    video_A = str(file_A)
    pitches = handler.open_obj_from_meta(c.PITCH_NAME, video_A)
    for p in pitches:
        print("start: " + str(p[0]["sec"]) + ", end: " + str(p[-1]["sec"]))

def find_all_matches(file_A):
    print("finding matched for images")
    video_A = str(file_A)
    other_files_same_series = file_handler.get_all_other_videos_in_series(video_A)
    print(len(other_files_same_series))
    matches = {}
    hashes_A = handler.open_obj_from_meta(c.HASH_NAME, video_A)

    for file_B in other_files_same_series:
        video_B = str(file_B)
        print("comparing: " + video_A + ", against: " + video_B)
        hashes_B = handler.open_obj_from_meta(c.HASH_NAME, video_B)
        frames_matched = comparer.find_all_matches_hash(hashes_A, hashes_B, c.HASH_CUTOFF)
        
        for matched_item in frames_matched:
            count = matched_item["count"]
            if count not in matches:
                matches[count] = {"numberMatches": 0, "sec": matched_item["sec"]}
            matches[count]["numberMatches"] += 1
    sequences = extract_sequences(matches)
    
    # loop through sequences and annotate
    
    # timeIntervals = []
    # for ... 
    #timeIntervals.append(TimeInterval("00:00:00", "00:00:00"))
    #scenes = None
    #with open(segmentationFile) as json_file:
    #        data = json.load(json_file)
    #        scenes = data['scenes']
    #ann.set_presence_of_time_interval("fmatch, ", scenes, timeIntervals)

# Will find sequences of matches and filter out unrelevant sequences

def extract_sequences(matches): 
    list_matches = []
    recorded_sequences = []

    for k, v in matches.items():
        list_matches.append(v["sec"])
    list_matches.sort()

    current_sequence = {}
    prev_time = 0

    for match in list_matches:
        if not current_sequence:
            current_sequence = {"start": match, "end": None}
        elif prev_time + c.SEQUENCE_THRESHOLD >= match:
            current_sequence["end"] = match
        else:
            if current_sequence["end"] != None and current_sequence["end"] - current_sequence["start"] > c.MIN_LENGTH_SEQUENCE:
                recorded_sequences.append(current_sequence)
                current_sequence = {"start": match, "end": match}
            else:
                current_sequence = {"start": match, "end": None}
        prev_time = match
    if current_sequence["end"] != None and current_sequence["end"] - current_sequence["start"] > c.MIN_LENGTH_SEQUENCE:
        recorded_sequences.append(current_sequence)

    for recorded in recorded_sequences:
        print(recorded)

    return recorded_sequences
