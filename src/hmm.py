import json

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
    test = obs[5]
    numpy.delete(obs, 0)
    result = labels[5]
    model = HiddenMarkovModel.from_samples(MultivariateGaussianDistribution, 
                                            n_components=2,
                                            X=obs,
                                            labels=labels,
                                            algorithm='labeled')
    seq = numpy.array(test)
    hmm_predictions = model.predict(seq)

    print(''.join(str(seq)))
    print(str(result))
    print(''.join(map( str, hmm_predictions)))

if __name__ == "__main__":
    startHMM()
