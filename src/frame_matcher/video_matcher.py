
# ------------------------------------------------------------------------- #
# Find matches between two videos, each video represented by its fullpath   #
# The result is a list of number of matches with a timestamp in seconds     #
# The algorithm used is called hashing                                      #

import imagehash
from PIL import Image

import utils.constants as c
import utils.file_handler as file_handler

from . import frame_comparer as comparer


def find_all_matches_hash(file_A, file_B):
    video_A = str(file_A)
    video_B = str(file_B)
    print("comparing: " + video_A + ", against: " + video_B)
    frames_A = file_handler.get_framespaths_from_video(video_A)
    frames_B = file_handler.get_framespaths_from_video(video_B)
    frames_A.sort(key=lambda x: x.count, reverse=False)
    frames_B.sort(key=lambda x: x.count, reverse=False)

    hashes_A = {}
    hashes_B = {}
    result = []
    for frame_A in frames_A:
        if frame_A.count not in hashes_A:
            hash_A = imagehash.average_hash(Image.open(frame_A.fileName))
            hashes_A[frame_A.count] = hash_A

        for frame_B in frames_B:
            if frame_B.count not in hashes_B:
                hash_B = imagehash.average_hash(Image.open(frame_B.fileName))
                hashes_B[frame_B.count] = hash_B
            if hashes_A[frame_A.count] - hashes_B[frame_B.count] < c.HASH_CUTOFF:
                result.append({"count": frame_A.count, "sec": frame_A.sec})
                break

    return result

# Compares a videofiles frames with frames related to all other videos within that directory
# Outputs a list of number of matches for a frame at a specific timeslot

def find_all_matches(file_A):
    other_files_same_series = file_handler.get_all_other_videos_in_series(file_A)
    matches = {}
    for file_B in other_files_same_series:
        frames_matched = find_all_matches_hash(file_A, file_B)
        for matched_item in frames_matched:
            count = matched_item["count"]
            if count not in matches:
                matches[count] = {"numberMatches": 0, "sec": matched_item["sec"]}
            matches[count]["numberMatches"] += 1
    for k, v in matches.items():
        print(str(k) + " - " + str(v))
