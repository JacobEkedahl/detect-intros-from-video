
"""
    This script will build the model based on the current dataset. This process may take a while to finish...
"""
import logging 
import time 
from datetime import datetime, date
import schedule 
import multiprocessing
import logging
import os
import json

from downloader import scrapesvt
from db import dataset_manager
from utils import constants
from frame_matcher import video_matcher
import db.video_repo as video_repo 
import preprocessing
import hmm



GENRES = constants.VIDEO_GENRES
SHOW = video_repo.SHOW_KEY
SEASON = video_repo.SEASON_KEY
PREPROCESSED = video_repo.PREPROCESSED_KEY
URL = video_repo.URL_KEY
PATH = video_repo.FULL_PATH_KEY

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


def __compare_video(video):
    start = datetime.now()
    video_matcher.find_all_matches(video[PATH])
    logging.info("Video comparison complete (%s), time taken: %s" % (video[URL], datetime.now()  - start))


def __predict_video(video):
    start = datetime.now()
    prediction = hmm.get_prediction(video[PATH])
    logging.info("Prediction complete (%s), time taken %s" % (prediction, datetime.now()  - start))


def start():

    logging.basicConfig(filename='log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    if not os.path.exists(DATASET_PATH):
        logging.warning("Path does not exist: %s " % DATASET_PATH)

    # Scrape Svt Play 
    __scrape_svt()

    # Import dataset annotations 
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
    preprocessedInSeason = 0
    for show in dictVideos:
        for season in dictVideos[show]:
            preprocessedInSeason = 0
            for video in dictVideos[show][season]:
                if not (PREPROCESSED in video and video[PREPROCESSED]):
                    try: 
                        result = preprocessing.preprocess_video(video)
                        if not result: 
                            logging.error("Failed to preprocess: %s" % video[URL])
                            count_failure = count_failure + 1 
                        else: 
                            count_success = count_success + 1 
                            preprocessedInSeason = preprocessedInSeason + 1
                    except Exception as e:
                        logging.exception(e)
                        count_failure = count_failure + 1 

            for video in dictVideos[show][season]:
                try: 
                    __compare_video(video)
                    __predict_video(video)
                except Exception as e: 
                    logging.exception(e)



