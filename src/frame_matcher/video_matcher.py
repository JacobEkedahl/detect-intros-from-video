
# ------------------------------------------------------------------------- #
# Find matches between two videos, each video represented by its fullpath   #
# The result is a list of number of matches with a timestamp in seconds     #
# The algorithm used is called hashing                                      #

import json
import logging
import pprint
import statistics

import imagehash
from PIL import Image

import annotations.annotate as ann
import utils.file_handler as file_handler
from annotations import annotate_meta as ann
from utils import (constants, extractor, object_handler, prob_calculator,
                   simple_segmentor, time_handler)

from . import frame_comparer as comparer

# Useful in case you change something about how the frame comparison works beyond changes to the threshold value and wish to apply it on all videos
ALWAYS_OVERRIDE_PREV_COMPARISON = False  


def __intro_has_changed(videofile, newIntro):
    video_data = file_handler.load_from_video_file(videofile)
    if "intro" in video_data:
        oldIntro = video_data["intro"]
        if oldIntro is None and newIntro is None:
            return False 
        if oldIntro is not None and (oldIntro["start"] == newIntro["start"] and oldIntro["end"] == newIntro["end"]):
            return False 
    elif newIntro is None: # There is no previous intro and the new one is none 
        return False 
    return True 

def find_all_matches(file_A):  
    video_A = str(file_A)    
    intro_median, matches, matches_intro = get_matches(video_A) 
    if len(intro_median) != 0 and matches_intro is not None:
        sequences_intro = get_best_intro(matches_intro)
        if sequences_intro is not None:
            ann.annotate_meta_data(sequences_intro, constants.DESCRIPTION_MATCHES_INTRO, video_A)

    best_seq = get_best_intro(matches)
    if best_seq is not None:
        ann.annotate_meta_data(best_seq, constants.DESCRIPTION_MATCHES, video_A)
    return best_seq

def get_matches(video_A):
    other_files_same_series = file_handler.get_neighboring_videos(video_A)
    matches = {}
    matches_intro = {}
    hashes_A = object_handler.open_obj_from_meta(constants.HASH_NAME, video_A)
    intro_median = []
    intro_start_median = []
    intros = []

    logging.info("comparing %s with:\n%s" % (video_A, other_files_same_series))

    should_make_new_comparison = ALWAYS_OVERRIDE_PREV_COMPARISON # Default 

    intro_A = extractor.get_intro_from_video(video_A)

    if __intro_has_changed(video_A, intro_A):
        logging.info("Intro has changed for A: %s " % video_A)
        should_make_new_comparison = True 
    file_handler.save_to_video_file(video_A, "intro", intro_A)

    for file_B in other_files_same_series:
        video_B = str(file_B)
        hashes_B = object_handler.open_obj_from_meta(constants.HASH_NAME, video_B)
        intro_B = extractor.get_intro_from_video(video_B)

        override_comparison = should_make_new_comparison # Default 

        # Check if intro for B has changed
        if __intro_has_changed(file_B, intro_B):
            logging.info("Intro has changed for B: %s " % file_B)
            override_comparison = True # Toggle to make a new comparison
        file_handler.save_to_video_file(file_B, "intro", intro_B)

        video_data = file_handler.load_from_video_file(video_A)
        # This part loads the frame comparison data for videofile A and checks to see if there is already a comparison between A and B. 
        # If no such comparison exists one is created and stored. 
        if "frame_matches" in video_data: 
            video_data_matches = video_data["frame_matches"]
        else: 
            video_data_matches = {}

        # If a previous comparison exists and we don't toggle automatic overriding -->
        if not override_comparison and file_B in video_data_matches:
            vide_data_matches_other_file = video_data_matches[file_B]
            frames_matched = vide_data_matches_other_file["frames_matched"]
            frames_matched_intro = vide_data_matches_other_file["frames_matched_intro"]
            # The threshold has changed from the previous comparison
            if not "threshold" in vide_data_matches_other_file or vide_data_matches_other_file["threshold"] != constants.HASH_CUTOFF: 
               override_comparison = True 
        else:
            override_comparison = True 

        # Overrides any previously existing comparison with a new comparison --> 
        if override_comparison:
            logging.info("Comparison is being made between %s and %s..." % (video_A, file_B))
            # Extracts frame hash comparison between file A and B.
            frames_matched, frames_matched_intro = comparer.find_all_matches_hash_intro(hashes_A, hashes_B, intro_B, constants.HASH_CUTOFF)
            vide_data_matches_other_file = {
                "intro": intro_B, 
                "threshold": constants.HASH_CUTOFF,
                "frames_matched": frames_matched,
                "frames_matched_intro": frames_matched_intro
            }
            video_data_matches[file_B] = vide_data_matches_other_file
            file_handler.save_to_video_file(video_A, "frame_matches", video_data_matches)

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

    return intro_median, matches, matches_intro

def get_best_intro(matches):
    sequences = extract_sequences(matches)
    sequences = sorted(sequences, key = lambda i: i['val'], reverse=True)
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
    if second_ranked["val"] / total > constants.FRACTION_SIZE_PREINTRO and second_ranked["start"] > highest_ranked["start"] and highest_ranked["start"] < constants.PREINTRO_START:
        return second_ranked
    else:
        return highest_ranked


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
        elif prev_time + constants.SEQUENCE_THRESHOLD >= match["sec"]:
            current_sequence["end"] = match["sec"]
            current_sequence["val"] = statistics.mean(last_seq_max) * (current_sequence["end"] - current_sequence["start"])
        else:
            if current_sequence["end"] != None and current_sequence["end"] - current_sequence["start"] > constants.MIN_LENGTH_SEQUENCE:
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
    if current_sequence and current_sequence["end"] != None and current_sequence["end"] - current_sequence["start"] > constants.MIN_LENGTH_SEQUENCE:
        recorded_sequences.append(current_sequence)

    return recorded_sequences

## method for testing the error rate of this intro finder
def find_errors():
    all_videos = file_handler.get_all_mp4_files()
    intros = extractor.get_intros_from_videos(all_videos)
    for i in range(0, len(all_videos), 8):
        video_file = all_videos[i]
        curr_intro = intros[i]
        s = find_all_matches(video_file)[0]
        i_start = time_handler.timestamp(curr_intro["start"]) /1000
        i_end = time_handler.timestamp(curr_intro["end"]) /1000
        diff_s = abs(s["start"] - i_start)
        diff_e = abs(s["end"] - i_end)
        print(video_file)
        print(str(diff_s) + " - " + str(diff_e))
