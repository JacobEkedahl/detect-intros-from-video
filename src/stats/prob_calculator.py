## Determines the probability of an sequence to be an intro
import statistics

import matplotlib.pyplot as plt
import numpy

from pomegranate import *
from utils import extractor, file_handler, time_handler


def get_most_probable_size(video_file):
    start_times, sizes = get_variables(video_file)
    return statistics.mean(sizes)

def get_variables(video_file):
    other_videos = file_handler.get_neighboring_videos(video_file)
    other_intros = extractor.get_intros_from_videos(other_videos)
    return get_start_times_and_sizes(other_intros) 

def guess_intro(video_file):
    obs, start_times, sizes = get_variables(video_file)
    most_starts = None
    try:
        most_starts = statistics.mode(start_times)
    except:
        most_starts = statistics.median(start_times)
    average_size = statistics.mean(sizes)
    end_time = most_starts + average_size
    return [{"start": most_starts, "end": end_time}]

def get_sequence_with_closest_size(sequences, video_file):
    avg_size = get_most_probable_size(video_file)
    min_diff = 1000
    cloesest_seq = None

    for seq in sequences:
        length = seq["end"] - seq["start"]
        diff = abs(avg_size - length)
        if diff < min_diff:
            min_diff = diff
            cloesest_seq = seq
    if cloesest_seq is not None:
        return [cloesest_seq]
    return []

def get_the_most_likely_sequence(sequences, list_of_intros):        
    obs, start_times, sizes = get_start_times_and_sizes(list_of_intros)
    times_dist = ExponentialDistribution.from_samples(start_times)
    sizes_dist = PoissonDistribution.from_samples(sizes)
    combined_mult = IndependentComponentsDistribution([times_dist, sizes_dist])

    best_result = -10000
    best_match = None
    for seq in sequences:
        start, size = convert_stamps_to_start_size(seq)
        pred = combined_mult.probability([start, size]) * 1000
        if pred > best_result:
            best_result = pred
            best_match = seq
    result = []
    if best_match is not None:
        print("best match: " + str(best_match))
        result.append(best_match)
    return result

def get_start_times_and_sizes(list_of_intros):
    intros = list_of_intros
    if list_of_intros is None:
        all_videos = file_handler.get_all_mp4_files()
        intros = extractor.get_intros_from_videos(all_videos)
    
    start_times = []
    sizes = []

    for intro in intros:
        start, size = convert_stamps_to_start_size(intro)
        if start is not None:
            sizes.append(size)
            start_times.append(start)
    return (start_times, sizes)

def convert_stamps_to_start_size(entry): 
    if entry["end"] == "00:00:00":
        return None, None

    res = type(entry["start"]) == str
    start = entry["start"]
    end = entry["start"]
    if res:
        start = time_handler.timestamp(entry["start"]) / 1000
        end = time_handler.timestamp(entry["end"]) / 1000

    size = abs(end - start)
    return (start, size)

def print_dist(d1, d2):
    idxs = numpy.arange(0, 480, 0.1)
    # blue is starttimes and cyan is sizes
    p1 = list(map(d1.probability, idxs))
    p2 = list(map(d2.probability, idxs))
    plt.figure(figsize=(16, 5))
    plt.plot(idxs, p1, color='b'); plt.fill_between(idxs, 0, p1, facecolor='b', alpha=0.2)
    plt.plot(idxs, p2, color='c'); plt.fill_between(idxs, 0, p2, facecolor='c', alpha=0.2)
    plt.xlabel("Value", fontsize=14)
    plt.ylabel("Probability", fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.show()


#    times_dist = ExponentialDistribution.from_samples(start_times)
 #   sizes_dist = PoissonDistribution.from_samples(sizes)
  #  combined = IndependentComponentsDistribution([times_dist, sizes_dist])
    #print_dist(times_dist, sizes_dist)
