## Determines the probability of an sequence to be an intro
import statistics

import matplotlib.pyplot as plt
import numpy

from pomegranate import *
from utils import file_handler, time_handler


def get_most_probable_size(video_file):
    other_videos = file_handler.get_all_other_videos_in_series(video_file)
    other_intros = file_handler.get_intros_from_videos(other_videos)
    obs, start_times, sizes = get_start_times_and_sizes(other_intros) 
    return statistics.mean(sizes)

def fun_test():
    first_video = file_handler.get_all_mp4_files()[0]
    other_videos = file_handler.get_all_other_videos_in_series(first_video)
    other_intros = file_handler.get_intros_from_videos(other_videos)

def guess_intro(intros):
    obs, start_times, sizes = get_start_times_and_sizes(intros)
   # most_starts = statistics.mode(start_times)
    sizes_related_to_starts = []
  #  for o in obs:
       # if o[0] == average_start:
         #   sizes_related_to_starts.append(o[1])
    average_start = statistics.median(start_times)
    average_size = statistics.mean(sizes)
    print("median start: " + str(average_start) + ", avg size: " + str(average_size))
    end_time = average_start + average_size
    result = []
    result.append({"start": average_start, "end": end_time})
    return result

def get_sequence_with_closest_size(sequences, list_of_intros):
    obs, start_times, sizes = get_start_times_and_sizes(list_of_intros)
    avg_size = statistics.mean(sizes)

    min_diff = 1000
    result = []
    cloesest_seq = None
    second_closest = None

    for seq in sequences:
        length = seq["end"] - seq["start"]
        diff = abs(avg_size - length)
        if diff < min_diff:
            min_diff = diff
            second_closest = cloesest_seq
            cloesest_seq = seq
    if second_closest is not None:
        result.append(second_closest)
    result.append(cloesest_seq)
    return result

def get_the_most_likely_sequence(sequences, list_of_intros):        
    obs, start_times, sizes = get_start_times_and_sizes(list_of_intros)
    times_dist = ExponentialDistribution.from_samples(start_times)
    sizes_dist = PoissonDistribution.from_samples(sizes)
    combined_mult = IndependentComponentsDistribution([times_dist, sizes_dist])
    #print_dist(times_dist, sizes_dist)
    #combined_mult = MultivariateGaussianDistribution.from_samples(numpy.array(obs))
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
        intros = file_handler.get_intros()
    
    start_times = []
    sizes = []
    obs = []

    for intro in intros:
        if intro["end"] != "00:00:00":
            start, size = convert_stamps_to_start_size(intro)
            obs.append([start, size])
            sizes.append(size)
            start_times.append(start)
    return (obs, start_times, sizes)

def convert_stamps_to_start_size(entry):  
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
