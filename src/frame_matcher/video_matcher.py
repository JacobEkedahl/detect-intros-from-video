
# ------------------------------------------------------------------------- #
# Find matches between two videos, each video represented by its fullpath   #
# The result is a list of number of matches with a timestamp in seconds     #
# The algorithm used is called hashing                                      #

import json
import statistics

import imagehash
from PIL import Image

import annotations.annotate as ann
import utils.file_handler as file_handler
from annotations import annotate_meta as ann
from segmenter import simple_segmentor
from utils import constants as c
from utils import extractor
from utils import object_handler as handler
from utils import time_handler

from . import frame_comparer as comparer


def find_matches_correlates_with_intro(file_A):
    video_A = str(file_A)
    other_files_same_series = file_handler.get_all_other_videos_in_series(video_A)
    # extract the intros of the other series, then when a match is found set a flag on whether or not
    # it matches with an frame that is within the intro
    # filter sequences and return the sequence with the most amount of flags set for intro matches
    return None

def find_all_matches(file_A):
    print("finding matched for images")
    video_A = str(file_A)
    other_files_same_series = file_handler.get_all_other_videos_in_series(video_A)
    matches = {}
    matches_intro = {}
    hashes_A = handler.open_obj_from_meta(c.HASH_NAME, video_A)
    intro_median = []

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

        intro_B = extractor.get_intro_from_video(video_B)
        intro_median.append(intro_B["end"] - intro_B["start"])
        if intro_B is not None:
            frames_matched_intro = comparer.find_all_matches_hash_intro(hashes_A, hashes_B, intro_B, c.HASH_CUTOFF)
            for matched_item in frames_matched_intro:
                count = matched_item["count"]
                if count not in matches_intro:
                    matches_intro[count] = {"numberMatches": 0, "sec": matched_item["sec"]}
                matches_intro[count]["numberMatches"] += 1

    sequences_intro = extract_sequences(matches_intro)
    seq_intro = get_sequence_closest_to_intro(sequences_intro, statistics.median(intro_median))
    sequences = extract_sequences(matches)
    ann.annotate_meta_data(sequences, c.DESCRIPTION_MATCHES, video_A)
    ann.annotate_meta_data(seq_intro, c.DESCRIPTION_MATCHES_INTRO, video_A)

def get_sequence_closest_to_intro(sequences, intro_length):
    min_diff = 1000
    result = []
    cloesest_seq = {}

    for seq in sequences:
        length = seq["end"] - seq["start"]
        diff = abs(intro_length - length)
        if diff < min_diff:
            min_diff = diff
            cloesest_seq = seq
    result.append(cloesest_seq)
    return result

def get_longest_sequence(sequences):
    longest_count = 0
    longest_seq = {}

    for seq in sequences:
        length = seq["end"] - seq["start"]
        if length > longest_count:
            longest_count = length
            longest_seq = seq
    return longest_seq

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
    if current_sequence and current_sequence["end"] != None and current_sequence["end"] - current_sequence["start"] > c.MIN_LENGTH_SEQUENCE:
        recorded_sequences.append(current_sequence)

    for recorded in recorded_sequences:
        print(recorded)

    return recorded_sequences
