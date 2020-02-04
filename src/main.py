import logging
import os
import pprint
import sys as s
from commands import cmd_dataset

import db.show_repo as show_repo
import db.video_repo as video_repo
import downloader.scrapesvt as scrapesvt
import pipeline
import predicting
import preprocessing
import rebuild
import stats.intro_stats as intro_stats
import stats.matches_stats as matches_stats
import utils.file_handler as file_handler
from api import app
from downloader import svtplaywrapper
from frame_matcher import frame_comparer as comparer
from frame_matcher import video_matcher as v_matcher
from frame_matcher import video_to_hashes as vf
from utils import cleaner, extractor, prob_calculator

if __name__ == "__main__":

    # Notice: 
    # Because logging is separated into 3 files: prediction.py, rebuild.py and preprocessing.py no log configurations can be in main for those commands. 
    # 
    file_handler.create_folderstructure_if_not_exists()

    if (len(s.argv) - 1 < 1):
        print("need more arguments! e.g: --dlv URL")
        exit()
        
    elif (s.argv[1] == "--clean"):
        if s.argv[2] == "--series":
            cleaner.remove_annotation_from_series(s.argv[3], s.argv[4])
        elif s.argv[2] == "--all":
            cleaner.remove_annotations(s.argv[3])
        elif s.argv[2] == "--format":
            if s.argv[3] == "--file":
                cleaner.format_file(s.argv[4])
            else:
                cleaner.reformat_segmentation_files()
    elif (s.argv[1] == "--testMatcher"):
        v_matcher.find_errors()
    elif (s.argv[1] == "--build"):
        try:
            if "--f" in s.argv:
                pipeline.build_dataset_from_step(s.argv[2], s.argv[3], True)
            else:
                pipeline.build_dataset_from_step(s.argv[2], s.argv[3], False)
        except Exception as e:
            print(e)  
            print("restarting..")  
            python = s.executable
            os.execl(python, python, ' '.join(s.argv))
            exit()
        exit()
    elif (s.argv[1] == "--match"):
        if len(s.argv) > 2:
            if s.argv[2] == "--file":
                file_one = s.argv[3]
                v_matcher.find_all_matches(file_one)
                exit()
                
    elif (s.argv[1] == "--dlv"):
        svtplaywrapper.download_video(s.argv[2])

    elif (s.argv[1] == "--dataset"):
        cmd_dataset.execute(s.argv)
        exit()

    elif (s.argv[1] == "--api"):
        app.start()
        exit()

    elif(s.argv[1] == "--work"): 
        preprocessing.start_schedule()
        exit(0)

    elif(s.argv[1] == "--predict"):
        url = s.argv[2]
        prediction = predicting.get_prediction_by_url(url)
        # STDOUT READ BY API #
        print("_PREDICTION_")
        print(prediction)
        exit(0)
    elif(s.argv[1] == "--rebuild"): 
        rebuild.start()
        exit(0)
        
    elif s.argv[1] == "--hist-intro":
        intro_stats.plot_hist_frequency()
    elif s.argv[1] == "--intro-ss":
        intro_stats.plot_intros()
    elif s.argv[1] == "--intro-sizes":
        intro_stats.plot_hist_sizes()
    elif s.argv[1] == "--intro":
        intro_stats.plot_all_intros()
    elif s.argv[1] == "--filtering-1":
        matches_stats.plot_frequencies()
    elif s.argv[1] == "--filtering-2":
        matches_stats.plot_filtering()
    elif s.argv[1] == "--filtering-3":
        matches_stats.plot_last_sequence()
    elif s.argv[1] == "--matches-n":
        matches_stats.plot_neighbors_frequencies()
    elif s.argv[1] == "--hash_threshold":
        matches_stats.plot_diff_threshold_hashes()

    else:
        print("no valid arguments found: " + str(s.argv))
