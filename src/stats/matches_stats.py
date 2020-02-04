import pprint
import random

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

import frame_matcher.video_matcher as video_matcher
from utils import constants, extractor, file_handler, time_handler

COMPFILE = constants.STATS_FILE
ERROR_MSG = "Set STATS_FILE in src/utils/constants to a valid filepath of a video in your dataset!"

def get_x_y(list_of_matches):
    [d['sec'] for d in list_of_matches]
    y_data = [d['numberMatches'] for d in list_of_matches]
    return {"x": x_data, "y": y_data}

def get_only_x(list_of_matches):
    all_amounts = [d['numberMatches'] for d in list_of_matches]
    all_x = []
    i = 0
    for amount in all_amounts:
        for y in range(amount):
            all_x.append(list_of_matches[i]["sec"])

        i+=1
    return all_x

def get_data_for_plotting(matches):
    matches_x = get_only_x(list(matches.values()))
    return matches_x

def get_rectangles_seq(sequences, color):
    result = []
    for seq in sequences:
        width = (seq["end"] - seq["start"])
        result.append({"start": (seq["start"], 0), "height": width, "width": seq["val"], "color": color})
    return result

def plot_sequences_as_rect(rects, rects_intro):
    plt.axes()
    label_matches_set = False
    label_matches_intro_set = False

    for rect in rects:
        if not label_matches_set:
            label_matches_set = True
            rectangle = plt.Rectangle(rect["start"], rect["height"], rect["width"], fc=rect['color'], label="F")
        else:
            rectangle = plt.Rectangle(rect["start"], rect["height"], rect["width"], fc=rect['color'])
        
        plt.gca().add_patch(rectangle)
    for rect in rects_intro:
        if not label_matches_intro_set:
            label_matches_intro_set = True
            rectangle = plt.Rectangle(rect["start"], rect["height"], rect["width"], fc=rect['color'], label="I")
        else:
            rectangle = plt.Rectangle(rect["start"], rect["height"], rect["width"], fc=rect['color'])
        
        plt.gca().add_patch(rectangle)
    plt.xlim(0, 480)
    plt.ylim(0, 60)
    plt.grid(True)
    plt.legend(loc = 'upper right')
    # naming the x axis
    plt.xlabel('Time (Seconds)') 
    # naming the y axis 
    plt.ylabel('Score')
    plt.show()
    

def plot_sequences_as_rect_axs(axs,fig, rects, rects_intro):
    plt.axes()
    label_matches_set = False
    label_matches_intro_set = False

    for rect in rects:
        if not label_matches_set:
            label_matches_set = True
            rectangle = plt.Rectangle(rect["start"], rect["height"], rect["width"], fc=rect['color'], label="F")
        else:
            rectangle = plt.Rectangle(rect["start"], rect["height"], rect["width"], fc=rect['color'])
        
        plt.gca().add_patch(rectangle)
    for rect in rects_intro:
        if not label_matches_intro_set:
            label_matches_intro_set = True
            rectangle = plt.Rectangle(rect["start"], rect["height"], rect["width"], fc=rect['color'], label="I")
        else:
            rectangle = plt.Rectangle(rect["start"], rect["height"], rect["width"], fc=rect['color'])
        
        plt.gca().add_patch(rectangle)
    plt.xlim(0, 480)
    plt.ylim(0, 60)
    plt.grid(True)
    plt.legend(loc = 'upper right')
    # naming the x axis
    plt.xlabel('Time (Seconds)') 
    # naming the y axis 
    plt.ylabel('Score')  

def plot_last_sequence():
    if COMPFILE is None:
        print(ERROR_MSG)
        exit()

    intro_median, matches, matches_intro = video_matcher.get_matches(COMPFILE)
    matches_best_seq = video_matcher.get_best_intro(matches)
    matches_best_seq_intro = video_matcher.get_best_intro(matches_intro)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(matches_best_seq)

    rects = get_rectangles_seq(matches_best_seq, 'blue')
    rects_intro = get_rectangles_seq(matches_best_seq_intro, 'orange')
    plot_sequences_as_rect(rects, rects_intro)


def plot_sequences():
    if COMPFILE is None:
        print(ERROR_MSG)
        exit()

    intro_median, matches, matches_intro = video_matcher.get_matches(COMPFILE)
    sequences_matches = video_matcher.extract_sequences(matches)
    sequences_matches_intro = video_matcher.extract_sequences(matches_intro)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(sequences_matches)

    rects = get_rectangles_seq(sequences_matches, 'blue')
    rects_intro = get_rectangles_seq(sequences_matches_intro, 'orange')
    plot_sequences_as_rect(rects, rects_intro)

def plot_filtering():
    if COMPFILE is None:
        print(ERROR_MSG)
        exit()

    #setup
    x_titles = ['Start time of intro (Seconds)', 'Length of intro (Seconds)']
    y_title = ['Frequency', 'Score']
    titles = ['Extraction of matches','Extraction of sequences', 'Choosing best sequence']
    colors = ['blue', 'orange']
    labels = [["F", "I"], []]

    intro_median, matches, matches_intro = video_matcher.get_matches(COMPFILE)

    #first
    data_matches = get_data_for_plotting(matches)
    data_matches_intro = get_data_for_plotting(matches_intro)

    #second
    sequences_matches = video_matcher.extract_sequences(matches)
    sequences_matches_intro = video_matcher.extract_sequences(matches_intro)
    
    rects = get_rectangles_seq(sequences_matches, 'blue')
    rects_intro = get_rectangles_seq(sequences_matches_intro, 'orange')

    bins = [40]
    x_data = [[data_matches, data_matches_intro]]
    fig, axs = plt.subplots(1, 2)
    axs = axs.ravel()

    for idx, ax in enumerate(axs):
        if idx == 0:
            x = x_data[idx]
            label = labels[idx]
            ax.hist(x[0], bins=bins[idx], label='F', fc=colors[0])
            ax.hist(x[1], bins=bins[idx], label='I', fc=colors[0]) 
            ax.set_title(titles[idx])
            ax.set_xlabel(x_titles[idx])
            ax.set_ylabel(y_title)
            ax.legend(loc = 'upper right')
            ax.grid()
        elif idx == 1:
            plot_sequences_as_rect_axs(ax, fig, rects, rects_intro)
            ax.relim()
            ax.autoscale_view()

    plt.tight_layout()
    plt.show()
    
def plot_diff_threshold_hashes():
    if COMPFILE is None:
        print(ERROR_MSG)
        exit()

    x_title = 'Time (Seconds)'
    y_title = 'Frequency'
    titles = ['Threshold equals 3','Threshold equals 4','Threshold equals 5','Threshold equals 6']
    labels = ["F", "I"]
    fig, axs = plt.subplots(2, 2)
    axs = axs.ravel()
    i = 1

    for idx, ax in enumerate(axs):
        constants.HASH_CUTOFF = idx+3
        intro_median, matches, matches_intro = video_matcher.get_matches(COMPFILE)
        data_matches = get_data_for_plotting(matches)
        data_matches_intro = get_data_for_plotting(matches_intro)
        ax.hist(data_matches, bins=40, label=labels[0], fc='blue')
        ax.hist(data_matches_intro, bins=40, label=labels[1], fc='orange')
        ax.set_title(titles[idx])
        ax.set_xlabel(x_title)
        ax.set_ylabel(y_title)
        ax.set_ylim(0, 130)
        ax.set_xlim(0, 480)
        ax.legend(loc = 'upper right')
        ax.grid()
    plt.tight_layout()
    plt.show()


def plot_neighbors_frequencies():
    if COMPFILE is None:
        print(ERROR_MSG)
        exit()

    x_title = 'Time (Seconds)'
    y_title = 'Frequency'
    titles = ['One neighbour','Two neighbours','Three neighbours','Four neighbours', 'Five neighbours', 'Six neighbours'] 
    labels = ["F", "I"]
    fig, axs = plt.subplots(3, 2)
    axs = axs.ravel()
    i = 1

    for idx, ax in enumerate(axs):
        constants.NUMBER_OF_NEIGHBOR_VIDEOS = idx+1
        intro_median, matches, matches_intro = video_matcher.get_matches(COMPFILE)
        data_matches = get_data_for_plotting(matches)
        data_matches_intro = get_data_for_plotting(matches_intro)
        ax.hist(data_matches, bins=40, label=labels[0], fc='blue')
        ax.hist(data_matches_intro, bins=40, label=labels[1], fc='orange')
        ax.set_title(titles[idx])
        ax.set_xlabel(x_title)
        ax.set_ylabel(y_title)
        ax.set_ylim(0, 130)
        ax.set_xlim(0, 480)
        ax.legend(loc = 'upper right')
        ax.grid()
    plt.tight_layout()
    plt.show()

def create_graph_freq():
    if COMPFILE is None:
        print(ERROR_MSG)
        exit()

    intro_median, matches, matches_intro = video_matcher.get_matches(COMPFILE)
    data_matches = get_data_for_plotting(matches)
    data_matches_intro = get_data_for_plotting(matches_intro)
    # naming the x axis
    plt.xlabel('Time (Seconds)') 
    # naming the y axis 
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.hist(data_matches, bins=40, label="F", fc='blue')
    plt.hist(data_matches_intro, bins=40, label="I", fc='orange') 
    plt.legend(loc = 'upper right')
    print(intro_median)

def plot_frequencies():
    create_graph_freq()
    plt.show()
