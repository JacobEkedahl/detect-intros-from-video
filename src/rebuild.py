
"""
    This script will build the model based on the current dataset. This process may take a while to finish...

    Suggested Future Changes: 
        - Make the web scraping directly from the video url, making it more decentralized and reduces initial bottleneck.    
"""
import json
import logging
import multiprocessing
import os
import time
from datetime import date, datetime

import hmm
import preprocessing
import schedule
from db import dataset_manager, video_repo
from downloader import scrapesvt
from frame_matcher import video_matcher
from utils import constants, time_handler

GENRES = constants.VIDEO_GENRES
SHOW = video_repo.SHOW_KEY
SEASON = video_repo.SEASON_KEY
PREPROCESSED = video_repo.PREPROCESSED_KEY
URL = video_repo.URL_KEY
PATH = video_repo.FULL_PATH_KEY
ANN_INTRO = video_repo.INTRO_ANNOTATION_KEY
START = "start"
END = "end"
DATASET_PATH = "data/dataset.json"

def __scrape_svt():
    start = datetime.now()
    scrapesvt.scrape_genres(GENRES)
    logging.info("scraping complete, time taken: %s" % (datetime.now()  - start))


def __import_dataset():
    start = datetime.now()
    dataset_manager.import_dataset(DATASET_PATH)
    logging.info("Dataset imported, time taken: %s" % (datetime.now()  - start))


def __export_dataset():
    start = datetime.now()
    dataset_manager.export_dataset(DATASET_PATH)
    logging.info("Dataset exported, time taken: %s" % (datetime.now()  - start))

def __rebuild_model():
    start = datetime.now()
    hmm.generate_model()
    logging.info("Hidden markov modell trained and saved, time taken: %s" % (datetime.now()  - start))

def __compare_video(video):
    start = datetime.now()
    video_matcher.find_all_matches(video[PATH])
    logging.info("Video comparison complete, time taken: %s" % (datetime.now()  - start))


def __make_time_interval_human_readable(timeInterval):
    return {
        START: time_handler.seconds_to_str(timeInterval[START]).split(":", 1)[1], 
        END: time_handler.seconds_to_str(timeInterval[END]).split(":", 1)[1]
    }

def __make_predictions_human_readable(predictions):
    outputList = []
    for p in predictions: 
        outputList.append(__make_time_interval_human_readable(p))
    return outputList


def __predict_video(video):
    start = datetime.now()
    predictions = hmm.get_prediction(video[PATH])
    logging.info("prediction complete, time taken %s" % (datetime.now()  - start))
    return predictions 

def start():
    logging.basicConfig(filename='rebuild.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    if not os.path.exists(DATASET_PATH):
        logging.warning("Path does not exist: %s " % DATASET_PATH)

    # Scrape Svt Play 
    __scrape_svt()

    # Import dataset annotations from file 
    __import_dataset()
    
    # Export dataset annotations - in case more have been added 
    # This step was added to support the current implementation of video_matcher
    __export_dataset()

    # Fetch and organize videos by show and season 
    videos = video_repo.find_all_with_intro_annotation()
    dictVideos = {}
    for video in videos: 
        show = video[SHOW]
        season = video[SEASON]
        if not show in dictVideos:
            dictVideos[show] = {}
        if not season in dictVideos[show]:
            dictVideos[show][season] = []
        dictVideos[show][season].append(video)

    # Iterate through all ordered videos 
    count_failure = 0
    count_success = 0
    video_managed = 0
    
    for show in dictVideos:
        for season in dictVideos[show]:
            for video in dictVideos[show][season]:
                video_managed = video_managed + 1
                logging.info("%.2f%% completed" % (video_managed/len(videos)*100)) 
                if not (PREPROCESSED in video and video[PREPROCESSED]):
                    try: 
                        result = preprocessing.preprocess_video(video)
                        if not result: 
                            logging.error("Failed to preprocess: %s" % video[URL])
                            count_failure = count_failure + 1 
                        else: 
                            count_success = count_success + 1 
                    except Exception as e:
                        logging.exception(e)
                        count_failure = count_failure + 1

        for video in dictVideos[show][season]:
            try:
                __compare_video(video)
            except Exception as e: 
                logging.exception(e)

    try:
        __rebuild_model()
    except Exception as e:
        logging.exception(e)
