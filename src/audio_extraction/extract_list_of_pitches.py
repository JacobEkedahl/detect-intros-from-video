import pprint

import matplotlib.pyplot as plt
import numpy as np

import parselmouth
from annotations import annotate_meta
from frame_matcher import video_matcher
from utils import constants


# load PRAAT pitches
def get_valid_pitches(audio_file):
    snd = parselmouth.Sound(str(audio_file))
    pitch = snd.to_pitch()
    frames = pitch.get_number_of_frames()
    start = pitch.get_start_time()
    end = pitch.get_total_duration()
    result = []
    for v_index in range(0, int(end) * 10, 1):
        time = v_index / 10
        curr_pitch = pitch.get_value_at_time(time)
        if str(curr_pitch) != "nan":
            result.append({"count": v_index, "val": curr_pitch, "sec": time})
    return get_longest_sequence(clean_result(result))

# not in use atm
def get_longest_sequence(sequences):
    longest_count = 0
    longest_seq = {}
    result = []

    for seq in sequences:
        length = seq["end"] - seq["start"]
        if length > longest_count:
            longest_count = length
            longest_seq = seq
    result.append(longest_seq)
    return result


def clean_result(pitches):
    list_of_seq = []
    margin = constants.MARGIN_BETWEEN_PITCH
    currentSeq = []
    for pitch in pitches:
        #print(str(pitch))
        if len(currentSeq) == 0:
            currentSeq.append(pitch)
        elif currentSeq[-1]["sec"] + margin >= pitch["sec"]:
            currentSeq.append(pitch)
        else:
            if len(currentSeq) > constants.MAX_SEQ_LENGTH_PITCH * 10:
                list_of_seq.append({"start": currentSeq[0]["sec"], "end": currentSeq[-1]["sec"]})
            currentSeq = []
    return list_of_seq
