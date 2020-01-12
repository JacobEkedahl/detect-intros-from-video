import json
import random
import statistics
import sys as s

import matplotlib.pyplot as plt
import numpy

from pomegranate import *
from stats import prob_calculator
from utils import constants, file_handler

import seaborn; seaborn.set_style('whitegrid')
seed = constants.START_SEED

def get_prediction(video_file):
    obs, labels = get_dataset_for_hmm()
    model = get_model(obs, labels)
    seg_file = file_handler.get_seg_file_from_video(video_file)
    with open(seg_file) as json_file:
        data = json.load(json_file)
        current_scenes = []
        for scene in data['scenes']:
            entry = []
            if 'matches' in scene:
                if scene['matches'] == True:
                    entry.append(1)
                else:
                    entry.append(0)
            else:
                entry.append(None)
            if 'matches_intro' in scene:
                if scene['matches_intro'] == True:
                    entry.append(1)
                else:
                    entry.append(0)
            else:
                entry.append(None)
            current_scenes.append(numpy.array(entry))
    hmm_predictions = model.predict(current_scenes)
    seq_pred = find_sequences_result(hmm_predictions)
    seq_pred = clean_sequences(seq_pred)
    most_likely_sequence = prob_calculator.get_sequence_with_closest_size(seq_pred, video_file)
    print(most_likely_sequence)
    return most_likely_sequence
                

def get_model(obs, labels):
    return HiddenMarkovModel.from_samples(MultivariateGaussianDistribution, 
                                            n_components=2,
                                            X=obs,
                                            labels=labels,
                                            state_names=["intro", "non"],
                                            algorithm='labeled')


def evaluate():
    total_start = []
    total_end = []
    curr_no_pred = []
    single_pred_list = []
    for i in range(10):
        global seed
        seed = i+3
        start_err, end_err, fraq_pred, single_pred = startHMM()
        total_start.extend(start_err)
        total_end.extend(end_err)
        single_pred_list.append(single_pred)
        curr_no_pred.append(fraq_pred)
    print("end result:")
    print("fraq success pred: " + str(statistics.mean(curr_no_pred)))
    print("fraq single pred: " + str(statistics.mean(single_pred_list)))
    evaluate_result(total_start, total_end)

def get_dataset_for_hmm():
    segFiles = []
    mp4s = file_handler.get_all_mp4_files()
    result = []
    data_labels = []
    for video_file in mp4s:
        segFiles.append(file_handler.get_seg_file_from_video(video_file))
    for seg_file in segFiles:  
        with open(seg_file) as json_file:
            count = 0
            current_scenes = []
            labels = []
            data = json.load(json_file)
            if 'intro' in data['scenes'][0]:
                for scene in data['scenes']:
                    entry = []
                    if 'matches' in scene:
                        if scene['matches'] == True:
                            entry.append(1)
                        else:
                            entry.append(0)
                    else:
                        entry.append(None)
                    if 'matches_intro' in scene:
                        if scene['matches_intro'] == True:
                            entry.append(1)
                        else:
                            entry.append(0)
                    else:
                        entry.append(None)

                    current_scenes.append(numpy.array(entry))
                    if not scene['intro']:
                        labels.append("non") 
                    else:
                        labels.append("intro")
            if len(current_scenes) != 0:
                result.append(numpy.array(current_scenes))
                data_labels.append(labels)
    return result, data_labels

def swap_entries(result, data_labels):
    global seed
    random.seed(seed)

    for i in range(len(result)):
        random_index = random.randint(0, len(result) - 1)
        swap_positions(result, data_labels, i, random_index)
    return result, data_labels

def swap_positions(data, labels, pos1, pos2):
    get = data[pos1], data[pos2] 
    data[pos2], data[pos1] = get 
    get = labels[pos1], labels[pos2] 
    labels[pos2], labels[pos1] = get 
    return data, labels
    
def startHMM():
    obs, labels = get_dataset_for_hmm()
    obs, labels = swap_entries(obs, labels)
    len_of_training = int(len(obs) * constants.TRAIN_SIZE)
    len_of_test = len(obs) - len_of_training
    trainX, trainY = obs[:len_of_training], labels[:len_of_training]
    testX, testY = obs[-len_of_test:], labels[-len_of_test:]
    model = get_model(trainX, trainY)
    
    matched_seq = []
    for i in testX:
        temp = []
        for x in i:
            temp.append(x[1])
        matched_seq.append(temp)

    diff_start = []
    diff_end = []
    predictions = 0
    no_pred = 0
    single_pred = 0
    for test_i in range(0,len(testX), 1):
        test = testX[test_i]
        result = testY[test_i]
        seq = numpy.array(test)
        hmm_predictions = model.predict(seq)
        seq_real = find_sequences(result)
        try:
            one_res = seq_real[0]
            seq_pred = find_sequences_result(hmm_predictions)
            seq_pred = clean_sequences(seq_pred)
            closest_pred = {}
            dist = 1000000
            dist_end = 10
            predictions += 1
            
            if len(seq_pred) != 0:
                if len(seq_pred) == 1:
                    single_pred += 1
            else:
                continue

            for pre in seq_pred:
                diff = abs(pre["start"] - one_res["start"])
                if diff < dist:
                    dist_end = abs(pre["end"] - one_res["end"])
                    closest_pred = pre
                    dist = diff

            if dist + dist_end > 20:
                print("real: " + str(one_res['start']) + " - " + str(one_res["end"]) + ", pred: " + str(seq_pred))
            else:
                no_pred += 1
                diff_start.append(dist)
                diff_end.append(dist_end)
        except:
            print("no true result in this one")
            
    evaluate_result(diff_start, diff_end)
    fraq_no_pred = no_pred / predictions
    freq_single_pred = single_pred / predictions
    print("fraq: " + str(fraq_no_pred))
    return diff_start, diff_end, fraq_no_pred, freq_single_pred

def evaluate_result(start_err, end_err):
    avg_start = statistics.mean(start_err)
    avg_end = statistics.mean(end_err)
    med_start = statistics.median(start_err)
    med_end = statistics.median(end_err)
    std_start = statistics.stdev(start_err)
    std_end = statistics.stdev(end_err)
    print("avg start err: " + str(avg_start) + ", avg end err: " + str(avg_end))
    print("median start err: " + str(med_start) + ", median end err: " + str(med_end))
    print("std start err: " + str(std_start) + ", std end err: " + str(std_end))


def find_sequences_result(list_of_ones_and_zeroes):
    found_one = False
    curr_seq = {}
    result = []
    for i in range(len(list_of_ones_and_zeroes)):
        entry = list_of_ones_and_zeroes[i] == 0
        if entry == 1 and found_one == False:
            curr_seq["start"] = i / 10
            found_one = True
        elif entry == 0 and found_one == True:
            curr_seq["end"] = i/ 10
            found_one = False
            result.append(curr_seq)
            curr_seq = {}
    if "end" in curr_seq:
        result.append(curr_seq)
    if len(result) == 0:
        print("no result in results")
        print(list_of_ones_and_zeroes)
    return result

def find_sequences(list_of_ones_and_zeroes):
    found_one = False
    curr_seq = {}
    result = []
    for i in range(len(list_of_ones_and_zeroes)):
        curr = list_of_ones_and_zeroes[i]
        entry = 1 if curr == "intro" else 0
        if entry == 1 and found_one == False:
            curr_seq["start"] = i / 10
            found_one = True
        elif entry == 0 and found_one == True:
            curr_seq["end"] = i/ 10
            found_one = False
            result.append(curr_seq)
            curr_seq = {}
    if "end" in curr_seq:
        result.append(curr_seq)
    if len(result) == 0:
        print("no result in seq")
    return result

def clean_sequences(sequences):
    newSeq = []
    if len(sequences) > 5:
        for i in range(len(sequences)):
            curr = sequences.pop(i)
            for j in range(i, len(sequences)):
                next_seq = sequences.pop(j)
                if curr["end"] - next_seq["start"] <= 0.2:
                    curr["end"] = next_seq["end"]
                else:
                    break
            newSeq.append(curr)
        return newSeq
    else:
        return sequences

if __name__ == "__main__":
    if len(s.argv) > 1:
        print("getting prediction")
        get_prediction(s.argv[1])
    else:
        evaluate()
