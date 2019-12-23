import pprint

import matplotlib.pyplot as plt
import numpy as np

import parselmouth

# load PRAAT pitches


def get_db(audio_file):
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
            #print("count: " + str(v_index) + ", sec: " + str(time) + ", val: " + str(curr_pitch))
            result.append({"count": v_index, "val": curr_pitch, "sec": time})
    return clean_result(result)

def clean_result(frequencies):
    list_of_seq = []
    margin = 1
    currentSeq = []
    for freq in frequencies:
        if len(currentSeq) == 0:
            currentSeq.append(freq)
        elif currentSeq[-1]["sec"] + margin >= freq["sec"]:
            currentSeq.append(freq)
        else:
            if len(currentSeq) > 50:
                list_of_seq.append(currentSeq)
            currentSeq = []
    return list_of_seq
