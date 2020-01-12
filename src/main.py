import logging 
import os
import pprint
import sys as s

from commands import cmd_segment, cmd_dataset, cmd_black

import preprocessing
import rebuild
import predicting

import pipeline
import downloader.scrapesvt as scrapesvt


import utils.file_handler as file_handler
from annotations import (annotation_summary, dataset_annotation,
                         scene_annotation)
from frame_matcher import frame_comparer as comparer
from frame_matcher import video_matcher as v_matcher
from frame_matcher import video_to_hashes as vf
from segmenter import scenedetector
from stats import prob_calculator
from utils import cleaner, extractor

from api import app

import db.video_repo as video_repo 
import db.show_repo as show_repo

if __name__ == "__main__":

    logging.basicConfig(filename='log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    file_handler.create_folderstructure_if_not_exists()

    if (len(s.argv) - 1 < 1):
        print("need more arguments! (--dlv --file nameOfTxtFile numberOfEpisodes)")
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
    elif (s.argv[1] == "--frames"):
        mp4_files = file_handler.get_all_mp4_files()
        for mp4_file in mp4_files:
            vf.save_hashes(str(mp4_file))
        exit()
    elif (s.argv[1] == "--match"):
        if len(s.argv) > 2:
            if s.argv[2] == "--file":
                file_one = s.argv[3]
                v_matcher.find_all_matches(file_one)
                exit()
    elif (s.argv[1] == "--compare"):
        if len(s.argv) > 2:
            if s.argv[2] == "--images":
                file_one = s.argv[3]
                file_two = s.argv[4]
                result = 0
                title = "Comparison"
                if "--orb" in s.argv:
                    result = comparer.compare_images_orb(file_one, file_two)
                    title = "Orb similarity"
                elif "--ssim" in s.argv:
                    result = comparer.compare_images_ssim(file_one, file_two)
                    title = "SSIM similarity"
                elif "--mse" in s.argv:
                    result = comparer.compare_images_mse(file_one, file_two)
                    title = "MSE similarity"
                elif "--hash" in s.argv:
                    result = comparer.compare_images_hash(file_one, file_two)
                    title = "HASH similarity"
                else:
                    result = comparer.compare_images_orb(file_one, file_two)
                    title = "Orb similarity"
                if "--plot" in s.argv:
                    img_a, img_b = comparer.read_images(file_one, file_two)
                    comparer.plot_comparison(img_a, img_b, title, result)
                print("similarity result: " + str(result))
 

    elif (s.argv[1] == "--seg"):
        cmd_segment.execute(s.argv)
        exit()
    
    elif (s.argv[1] == "--dataset"):
        cmd_dataset.execute(s.argv)
        exit()

    elif (s.argv[1] == "--black"):
        cmd_black.execute(s.argv)
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

    else:
        print("no valid arguments found: " + str(s.argv))
