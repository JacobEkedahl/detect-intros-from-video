import json
import os
import random
import statistics
import sys as s

import matplotlib.mlab as mlabnorm
import matplotlib.pyplot as plt
import scipy

from pomegranate import *
from sklearn.metrics import r2_score
from utils import constants, file_handler, prob_calculator

seed = constants.START_SEED

DATAFOLDERNAME = constants.TEMP_FOLDER_PATH
HMMMODEL = "hmm.json"


def get_saved_model():
    if not os.path.exists(get_full_path_model()):
        if not os.path.exists(get_full_path_data()):
            os.makedirs(get_full_path_data())
        generate_model()
    with open(get_full_path_model()) as json_file:
        data = json.load(json_file)
        return HiddenMarkovModel.from_json(data)

def generate_model():
    obs, labels = get_dataset_for_hmm()
    model = get_model(obs, labels)
    model_file = model.to_json()
    with open(get_full_path_model(), 'w') as outfile:
        json.dump(model_file, outfile, indent=4, sort_keys=False)
    
def get_full_path_data():
    return os.path.join(str(os.getcwd()), DATAFOLDERNAME)
    
def get_full_path_model():
    return os.path.join(str(os.getcwd()), DATAFOLDERNAME, HMMMODEL)

def get_prediction(video_file):
    model = get_saved_model()
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
                                            algorithm='viterbi',
                                            verbose=True)


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

def evaluate():
    total_start = []
    total_end = []
    curr_no_pred = []
    single_pred_list = []

    pred_start_list = []
    pred_end_list = []
    res_start_list = [] 
    res_end_list = [] 

    res_end = []
    true_pos = 0
    true_neg = 0
    false_pos = 0
    false_neg = 0

    for i in range(10):
        global seed
        seed = i+3
        start_err, end_err, fraq_pred, single_pred, true_positives, true_negatives, false_positives, false_negative, pred_start, pred_end, res_start, res_end = startHMM()
        total_start.extend(start_err)
        total_end.extend(end_err)
        single_pred_list.append(single_pred)
        curr_no_pred.append(fraq_pred)
        true_pos += true_positives
        true_neg += true_negatives
        false_pos += false_positives
        false_neg += false_negative
        pred_start_list.extend(pred_start)
        pred_end_list.extend(pred_end)
        res_start_list.extend(res_start)
        res_end_list.extend(res_end)
    print("end result:")
    print("fraq success pred: " + str(statistics.mean(curr_no_pred)))
    print("fraq single pred: " + str(statistics.mean(single_pred_list)))
    evaluate_result(total_start, total_end, pred_start_list, pred_end_list, res_start_list, res_end_list)
    evalute_classification(true_pos, true_neg, false_pos, false_neg)
    plot_error_margin(pred_start_list, pred_end_list, res_start_list, res_end_list)

def evalute_classification(true_pos, true_neg, false_pos, false_neg):
    ppv  = true_pos/(true_pos + false_pos)
    tpr = true_pos/(true_pos + false_neg)
    acc = (true_pos + true_neg) / ((true_pos + true_neg) + (false_pos + false_neg))
    print("true pos: " +  str(true_pos))
    print("true_neg: " +  str(true_neg))
    print("false_pos: " +  str(false_pos))
    print("false_neg: " +  str(false_neg))
    print("ppv: " +  str(ppv))
    print("tpr: " +  str(tpr))
    print("acc: " +  str(acc))
    
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

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negative = 0

    res_start = []
    pred_start = []
    res_end = []
    pred_end = []
    
    matched_seq = []
    for i in testX:
        temp = []
        for x in i:
            temp.append(x[0])
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
        hmm_predictions = model.predict(sequence=seq, algorithm='viterbi')
        seq_real = find_sequences(result)
        one_res = []
        if seq_real:
            one_res = seq_real[0]
        try:
            seq_pred = find_sequences_result(hmm_predictions)
            seq_pred = clean_sequences(seq_pred)
            closest_pred = {}
            dist = 44.5
            dist_end = 10
            predictions += 1

            if len(seq_pred) == 0 and len(one_res) == 0:
                print("success pred")
                true_negatives += 1
                single_pred += 1
                dist = 0
                dist_end = 0
            else:
                if len(one_res) == 0:
                    print(str(seq_pred))
                    single_pred += 1
                    dist = 30
                    dist_end = 30
                    

                elif len(seq_pred) >= 1: 
                    best_start_pred = 0
                    best_end_pred = 0
                    avg_length = one_res['end'] - one_res['start']
                    print(avg_length)

                    if len(seq_pred) == 1:
                        closest_pred = seq_pred[0]
                        single_pred += 1
                    else:
                        margin_to_avg = 10000000
                        for pre in seq_pred:
                            length_pred = abs(pre['end'] - pre['start'])
                            diff_length = abs(avg_length - length_pred)
                            if diff_length < margin_to_avg:
                                margin_to_avg = diff_length
                                closest_pred = pre

                    dist = abs(closest_pred["start"] - one_res["start"])
                    dist_end = abs(closest_pred["end"] - one_res["end"])
                    best_start_pred = closest_pred["start"]
                    best_end_pred = closest_pred["end"]

                    pred_start.append(best_start_pred)
                    pred_end.append(best_end_pred)
                    if one_res:
                        res_start.append(one_res["start"])
                        res_end.append(one_res["end"])

                if dist + dist_end > 20:
                    predVal = '0 - 0'
                    startOneRes = '0'
                    endOneRes = '0'

                    if not seq_real:
                        false_positives +=1
                    elif not seq_pred:
                        false_positives +=1
                    else:
                        false_negative += 1

                    if seq_pred:
                        predVal = str(seq_pred)
                    if one_res:
                        startOneRes = str(one_res['start'])
                        endOneRes = str(one_res["end"])
                    print("real: " + startOneRes + " - " + endOneRes + ", pred: " + predVal)
                else:
                    if seq_real or seq_pred: # wont happen
                        true_positives += 1
                    no_pred += 1
                    diff_start.append(dist)
                    diff_end.append(dist_end)
        except Exception as e:
            print("no true result in this one")
            print(e)
            raise e
            
    print(str(len(pred_start)) + " - " + str(len(res_start)))
    print(str(len(pred_end)) + " - " + str(len(res_end)))
    evaluate_result(diff_start, diff_end, pred_start, pred_end, res_start, res_end)
    evalute_classification(true_positives, true_negatives, false_positives, false_negative)
    fraq_no_pred = no_pred / predictions
    freq_single_pred = single_pred / predictions
    print("fraq: " + str(fraq_no_pred))
    return diff_start, diff_end, fraq_no_pred, freq_single_pred, true_positives, true_negatives, false_positives, false_negative, pred_start, pred_end, res_start, res_end

def evaluate_result(start_err, end_err, pred_start, pred_end, res_start, res_end):
    avg_start = statistics.mean(start_err)
    avg_end = statistics.mean(end_err)
    med_start = statistics.median(start_err)
    med_end = statistics.median(end_err)
    std_start = statistics.stdev(start_err)
    std_end = statistics.stdev(end_err)
    r2_start = r2_score(res_start, pred_start)
    r2_end = r2_score(res_end, pred_end)

    print("avg start err: " + str(avg_start) + ", avg end err: " + str(avg_end))
    print("median start err: " + str(med_start) + ", median end err: " + str(med_end))
    print("std start err: " + str(std_start) + ", std end err: " + str(std_end))
    print("r2 start: " + str(r2_start) + ", r2 end: " + str(r2_end))

def get_margin(pred_list_start, pred_list_end, real_list_start, real_list_end ):
    margin_start_list = []
    margin_end_list = []
    correct_predictions = 0
    for i in range(len(pred_list_start)):
        margin_start = pred_list_start[i]- real_list_start[i]
        margin_end = pred_list_end[i]- real_list_end[i]
        if abs(margin_start) + abs(margin_end) <= 20:
            margin_start_list.append(margin_start)
            margin_end_list.append(margin_end)
            correct_predictions += 1
    fraq = correct_predictions / len(pred_list_end)
    return margin_start_list, margin_end_list, fraq

def plot_error_margin(pred_start, pred_end, res_start, res_end):
    xstart, xend, fraq = get_margin(pred_start, pred_end, res_start, res_end)
    xlabels = [xstart, xend]

    colors = ['blue', 'orange']
    x_title = 'Prediction margin (Seconds)'
    y_title = 'Probability'
    titles = ['Start Prediction - Margin of error','End Prediction - Margin of error']
    fig, axs = plt.subplots(1, 2)
    axs = axs.ravel()
    
    for idx, ax in enumerate(axs):        
        x = xlabels[idx]
        (mu, sigma) = scipy.stats.norm.fit(x)
        print(str(mu))
        n, bins, patches = ax.hist(xlabels[idx], 60, normed=1, facecolor=colors[idx], alpha=0.75)
        y = scipy.stats.norm.pdf( bins, mu, sigma)

        ax.plot(bins, y, 'r--', linewidth=2)
        ax.set_title(titles[idx],fontsize=10)
        ax.set_xlabel(x_title)
        ax.set_ylabel(y_title)
        ax.grid()
        
    plt.tight_layout()
    plt.show()

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
    return result

def min_length_sequence(seq):
    return abs(seq['end'] - seq['start']) > 3

def remove_short_prediction(sequences):
    return [seq for seq in sequences if min_length_sequence(seq)]

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
        return remove_short_prediction(newSeq)
    else:
        return remove_short_prediction(sequences)

if __name__ == "__main__":
    if len(s.argv) > 1:
        print("getting prediction")
        get_prediction(s.argv[1])
    else:
        evaluate()
