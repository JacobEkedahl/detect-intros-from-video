
# ------------------------------------------------------------------------- #
# Find matches between two videos, each video represented by its fullpath   #
# The result is a list of number of matches with a timestamp in seconds     #
# The algorithm used is called hashing                                      #

import json
import pprint
import statistics

import imagehash
from PIL import Image

import annotations.annotate as ann
import utils.file_handler as file_handler
from annotations import annotate_meta as ann
from classifier import prob_calculator
from segmenter import simple_segmentor
from utils import constants as c
from utils import extractor
from utils import object_handler as handler
from utils import time_handler

from . import frame_comparer as comparer


def find_errors():
    all_videos = file_handler.get_all_mp4_files()
    intros = file_handler.get_intros_from_videos(all_videos)
    for i in range(0, len(all_videos), 8):
        video_file = all_videos[i]
        curr_intro = intros[i]
        s = find_all_matches(video_file)
        i_start = time_handler.timestamp(curr_intro["start"]) /1000
        i_end = time_handler.timestamp(curr_intro["end"]) /1000
        diff_s = abs(s["start"] - i_start)
        diff_e = abs(s["end"] - i_end)
        print(video_file)
        print(str(diff_s) + " - " + str(diff_e))
    
def find_all_matches(file_A):
    video_A = str(file_A)
    seg_file = file_handler.get_seg_file_from_video(video_A)
    with open(seg_file) as json_file:
        data = json.load(json_file)
        scenes = data['scenes']
        if 'matches' in scenes[0]:
            return

    other_files_same_series = file_handler.get_all_other_videos_in_series(video_A)
    matches = {}
    matches_intro = {}
    hashes_A = handler.open_obj_from_meta(c.HASH_NAME, video_A)
    intro_median = []
    intro_start_median = []
    intros = []

    for file_B in other_files_same_series:
        video_B = str(file_B)
        #print("comparing: " + video_A + ", against: " + video_B)
        hashes_B = handler.open_obj_from_meta(c.HASH_NAME, video_B)
        
        intro_B = extractor.get_intro_from_video(video_B)
        frames_matched, frames_matched_intro = comparer.find_all_matches_hash_intro(hashes_A, hashes_B, intro_B, c.HASH_CUTOFF)
        for matched_item in frames_matched:
            count = matched_item["count"]
            if count not in matches:
                matches[count] = {"numberMatches": 0, "sec": matched_item["sec"]}
            matches[count]["numberMatches"] += 1
            
        if len(frames_matched_intro) > 0:
            intro_median.append(intro_B["end"] - intro_B["start"])
            intro_start_median.append(intro_B["start"])
            for matched_item in frames_matched_intro:
                count = matched_item["count"]
                if count not in matches_intro:
                    matches_intro[count] = {"numberMatches": 0, "sec": matched_item["sec"]}
                matches_intro[count]["numberMatches"] += 1
            
    if len(intro_median) != 0 and matches_intro is not None:
        sequences_intro = get_best_intro(matches_intro)
        print("best intro: " + str(sequences_intro))
        if sequences_intro is not None:
            ann.annotate_meta_data(sequences_intro, c.DESCRIPTION_MATCHES_INTRO, video_A)

    best_seq = get_best_intro(matches)
    if best_seq is not None:
        ann.annotate_meta_data(best_seq, c.DESCRIPTION_MATCHES, video_A)
    return best_seq


def get_best_intro(matches):
    sequences = extract_sequences(matches)
    print(sequences)
    sequences = sorted(sequences, key = lambda i: i['val'], reverse=True)
   # print(sequences)
    if len(sequences) > 1:
        return [remove_preintro_if_present(sequences)]
    elif len(sequences) == 0:
        return None
    else:
        return [sequences[0]]

def remove_preintro_if_present(sequences):
    highest_ranked = sequences[0]
    second_ranked = sequences[1]
    total = highest_ranked["val"] + second_ranked["val"]
    if second_ranked["val"] / total > c.FRACTION_SIZE_PREINTRO and second_ranked["start"] > highest_ranked["start"] and highest_ranked["start"] < c.PREINTRO_START:
        return second_ranked
    else:
        return highest_ranked

def get_longest_sequence(sequences):
    longest_count = 0
    longest_seq = {}
    result = []

    for seq in sequences:
        length = seq["end"] - seq["start"]
        if length > longest_count:
            longest_count = length
            longest_seq = seq
    if 'start' not in longest_seq:
        return None
    result.append(longest_seq)
    return result

# Will find sequences of matches and filter out unrelevant sequences
def extract_sequences(matches): 
    list_matches = []
    recorded_sequences = []

    for k, v in matches.items():
        list_matches.append({"sec": v["sec"], "val": v["numberMatches"]})
    list_matches = sorted(list_matches, key = lambda i: i['sec']) 

    current_sequence = {}
    prev_time = 0
    last_seq_max = []
    end_seq = {}

    for match in list_matches:
        if not current_sequence:
            current_sequence = {"start": match["sec"], "end": None}
        elif prev_time + c.SEQUENCE_THRESHOLD >= match["sec"]:
            current_sequence["end"] = match["sec"]
            current_sequence["val"] = statistics.mean(last_seq_max) * (current_sequence["end"] - current_sequence["start"])
        else:
            if current_sequence["end"] != None and current_sequence["end"] - current_sequence["start"] > c.MIN_LENGTH_SEQUENCE:
                current_sequence["end"] = end_seq["sec"]
                recorded_sequences.append(current_sequence)
                current_sequence = {"start": match["sec"], "end": end_seq["sec"], "val": statistics.mean(last_seq_max) * (end_seq["sec"] - match["sec"])}
                last_seq_max = []
            else:
                current_sequence = {"start": match["sec"], "end": None, "val": statistics.mean(last_seq_max) * (end_seq["sec"] - match["sec"])}
                last_seq_max = []

        prev_time = match["sec"]
        last_seq_max.append(match["val"])
        most_pop = None
        try:
            most_pop = statistics.mode(last_seq_max)
        except:
            most_pop = statistics.median(last_seq_max)
        if match["val"] >= most_pop:
            end_seq = match
    if current_sequence and current_sequence["end"] != None and current_sequence["end"] - current_sequence["start"] > c.MIN_LENGTH_SEQUENCE:
        recorded_sequences.append(current_sequence)

    return recorded_sequences
