import json
import statistics

import matplotlib.pyplot as plt
import numpy

from pomegranate import *
from utils import file_handler

import seaborn; seaborn.set_style('whitegrid')

def get_dataset_for_hmm():
    segFiles = []
    mp4s = file_handler.get_all_mp4_files()
    result = []
    data_labels = []
    #print(mp4s[0])
    #exit()
    for video_file in mp4s:
        segFiles.append(file_handler.get_seg_file_from_video(video_file))
    for seg_file in segFiles:  
        count = 0
        current_scenes = []
        labels = []
        with open(seg_file) as json_file:
            data = json.load(json_file)
            if 'intro' not in data['scenes'][0]:
                continue
            for scene in data['scenes']:
              #  count += 1
              #  if count == 400:
              #      break
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

                if 'pitches' in scene:
                    if scene['pitches'] == True:
                        entry.append(1)
                    else:
                        entry.append(0)
                else:
                    entry.append(None)
                
                if 'subtitles' in scene:
                    if scene['subtitles'] == True:
                        entry.append(1)
                    else:
                        entry.append(0)
                else:
                    entry.append(None)
                
                current_scenes.append(numpy.array(entry))
                if scene['intro']:
                    labels.append(1) 
                else:
                    labels.append(0) 
        print(str(len(current_scenes)) + " - " + str(len(labels)))
        result.append(numpy.array(current_scenes))
        data_labels.append(labels)
    return result, data_labels
    
def startHMM():
    obs, labels = get_dataset_for_hmm()
    len_of_training = int(len(obs) * 0.7)
    len_of_test = len(obs) - len_of_training
    trainX, trainY = obs[:len_of_training], labels[:len_of_training]
    testX, testY = obs[-len_of_test:], labels[-len_of_test:]
    
    model = HiddenMarkovModel.from_samples(MultivariateGaussianDistribution, 
                                            n_components=2,
                                            X=trainX,
                                            labels=trainY,
                                            algorithm='labeled')
    diff_start = []
    diff_end = []
    print(len(testX))
    for test_i in range(0,len(testX), 1):
        test = testX[test_i]
        result = testY[test_i]
        seq = numpy.array(test)
        hmm_predictions = model.predict(seq)
        seq_real = find_sequences(result)
        try:
            one_res = seq_real[0]
            seq_pred = find_sequences(hmm_predictions)
            closest_pred = {}
            dist = 1000000
            dist_end = 10
            for pre in seq_pred:
                diff = abs(pre["start"] - one_res["start"])
                if diff < dist:
                    dist_end = abs(pre["end"] - one_res["end"])
                    closest_pred = pre
                    dist = diff
            diff_start.append(dist)
            diff_end.append(dist_end)
            print("real: " + str(one_res['start']) + " - " + str(one_res["end"]) + ", pred: " + str(seq_pred))
        except:
            print("no true result in this one")
            
    avg_start = statistics.mean(diff_start)
    avg_end = statistics.mean(diff_end)
    med_start = statistics.median(diff_start)
    med_end = statistics.median(diff_end)
    std_start = statistics.stdev(diff_start)
    std_end = statistics.stdev(diff_end)
    print("avg start err: " + str(avg_start) + ", avg end err: " + str(avg_end))
    print("median start err: " + str(med_start) + ", median end err: " + str(med_end))
    print("std start err: " + str(std_start) + ", std end err: " + str(std_end))

def find_sequences(list_of_ones_and_zeroes):
    found_one = False
    curr_seq = {}
    result = []
    for i in range(len(list_of_ones_and_zeroes)):
        entry = int(list_of_ones_and_zeroes[i])
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
    return result

if __name__ == "__main__":
    startHMM()
