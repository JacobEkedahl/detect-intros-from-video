"""
    Calling preprocessing.start_schedule() will scrape all videos from svtplay and begin the preprocessing process inbetween the allocated time window defined in constants. 
"""

import logging 

import time 
from datetime import datetime, date
import schedule 
import multiprocessing
import logging
import os

from utils import constants, file_handler 
import db.video_repo as video_repo 
import downloader.scrapesvt as scraper 
import downloader.svtplaywrapper as dl 
from segmenter import blackdetector, scenedetector, simple_segmentor
from annotations import annotate_black, annotate_scenes,annotate, annotate_intro
from frame_matcher import video_to_hashes, video_matcher

START_WORK = constants.SCHEDULED_PREPROCESSING_START
END_WORK = constants.SCHEDULED_PREPROCESSING_END
PENDING_CHECK_INTERVAL = 5
DEBUG = True 

GENRES = constants.VIDEO_GENRES
APPLY_BLACK_DETECTION = constants.APPLY_BLACK_DETECTION
APPLY_SCENE_DETECTION = constants.APPLY_SCENE_DETECTION


CPU_COUNT = multiprocessing.cpu_count()

SAVE_TO_FILE = constants.SAVE_TO_FILE
SAVE_TO_DB = constants.SAVE_TO_DB
DELETE_VIDEO_FILES_AFTER_EXTRACTION = constants.DELETE_VIDEO_AFTER_EXTRACTION

URL = video_repo.URL_KEY
PATH = video_repo.FULL_PATH_KEY
DL = video_repo.DOWNLOADED_KEY
FILE = video_repo.FILE_KEY
PREPROCESSED = video_repo.PREPROCESSED_KEY
SEGMENTS = video_repo.SEGMENTS_KEY


# This is a database free version of the below, returns false if the video download failed, throws an exception if any other part of the preprocess fails  
# Not really tested but something which may or may not be useful
def preprocess_url(url):
    try: 
        videofile = dl.download_video(url)
    except Exception as err: 
        logging.error(err)
        logging.error("failed to download: %s" % url)
        return False # We skip this video, try again at a later time 

    segments = simple_segmentor.segment_video(videofile)
    if APPLY_BLACK_DETECTION: 
        start = datetime.now()
        blackSequences, blackFrames = blackdetector.detect_blackness(videofile)
        segments = annotate_black.annotate_black_frames(segments, blackdetector.FRAME_KEY, blackFrames)
        segments = annotate_black.annotate_black_sequences(segments, blackdetector.SEQUENCE_KEY, blackSequences)
        segments = annotate_black.combine_annotation_into(segments, "black", blackdetector.SEQUENCE_KEY, blackSequences, blackdetector.FRAME_KEY, blackFrames, True)
        logging.info("blackdetection complete, time taken: %s" % (datetime.now()  - start))
    
    if APPLY_SCENE_DETECTION:
        start = datetime.now()
        scenes = scenedetector.detect_scenes(videofile)
        segments = annotate_scenes.annotate_detected_scenes(segments, scenes, scenedetector.DATA_KEY)
        logging.info("scenedetection complete, time taken: %s" % (datetime.now()  - start))

    start = datetime.now()
    video_to_hashes.save_hashes(videofile) 
    logging.info("hash extraction complete, time taken: %s" % (datetime.now()  - start))

    file_handler.save_to_video_file(videofile, simple_segmentor.SCENES_KEY, segments)

    return True # Success


def preprocess_video(video):
    start = datetime.now()
    logging.info("Preprocessing of video started at: %s", start)
    # if video was not downloaded --> download
    if not video[DL]:
        try: 
            videofile = dl.download_video(video[URL])
            if videofile: 
                video[DL] = True
                video[PATH] = videofile 
                video[FILE] = os.path.basename(videofile)
                entry = { DL: video[DL], PATH: video[PATH] , FILE:  video[FILE] } # save dl meta
                video_repo.set_many_by_url(video[URL], entry)
                logging.info("Download complete: %s, time taken: %s" % (videofile, datetime.now()  - start))
        except Exception as err: 
            logging.error(err)
            logging.error("failed to download: %s" % video[URL])
            if DEBUG: print(err)

            return False # We skip this video, try again on next schedule 
    else:
        videofile = video[video_repo.FULL_PATH_KEY]

    # if video was not pre-processed --> pre-process
    if not (video_repo.PREPROCESSED_KEY in video) or not (video[video_repo.PREPROCESSED_KEY]):

        segments = simple_segmentor.segment_video(videofile)

        if APPLY_BLACK_DETECTION: 
            start = datetime.now()
            blackSequences, blackFrames = blackdetector.detect_blackness(videofile)
            segments = annotate_black.annotate_black_frames(segments, blackdetector.FRAME_KEY, blackFrames)
            segments = annotate_black.annotate_black_sequences(segments, blackdetector.SEQUENCE_KEY, blackSequences)
            segments = annotate_black.combine_annotation_into(segments, "black", blackdetector.SEQUENCE_KEY, blackSequences, blackdetector.FRAME_KEY, blackFrames, True)
            logging.info("blackdetection complete, time taken: %s" % (datetime.now()  - start))
        
        if APPLY_SCENE_DETECTION:
            start = datetime.now()
            scenes = scenedetector.detect_scenes(videofile)
            segments = annotate_scenes.annotate_detected_scenes(segments, scenes, scenedetector.DATA_KEY)
            logging.info("scenedetection complete, time taken: %s" % (datetime.now()  - start))

        if video_repo.INTRO_ANNOTATION_KEY in video: 
            start = datetime.now()
            intro = video[video_repo.INTRO_ANNOTATION_KEY]
            segments = annotate_intro.apply_annotated_intro_on_segments(video[video_repo.URL_KEY], segments, intro)
            logging.info("intro annotation complete, time taken: %s" % (datetime.now()  - start))
            
        start = datetime.now()
        video_to_hashes.save_hashes(videofile) 
        logging.info("hash extraction complete, time taken: %s" % (datetime.now()  - start))

        video[SEGMENTS] = segments 
        video[PREPROCESSED] = True 
    
        # save changes to file 
        if SAVE_TO_FILE:
            file_handler.save_to_video_file(videofile, simple_segmentor.SCENES_KEY, segments)

        # Saves changes to database 
        video_repo.set_many_by_url(video[URL], {
            simple_segmentor.SCENES_KEY: video[SEGMENTS],
            PREPROCESSED: video[PREPROCESSED] 
        })

        if DELETE_VIDEO_FILES_AFTER_EXTRACTION:
            if os.path.exists(video[PATH]):
                os.remove(video[PATH])
            subs = video[PATH].replace("-converted.mp4", ".srt")
            if os.path.exists(subs):
                os.remove(video[PATH].replace("-converted.mp4", ".srt"))
    
def __get_start_end_time_now():
    start = START_WORK.split(":")
    end = END_WORK.split(":")
    now = datetime.now()
    start_time = now.replace(minute=int(start[1]), hour=int(start[0]))
    end_time = now.replace(minute=int(end[1]), hour=int(end[0]))

    if start_time > end_time: 
        end_time = now.replace(minute=int(start[1]), hour=int(start[0]), day=now.day + 1)

    return start_time, end_time, now


def do_work():

    start_time, end_time, now = __get_start_end_time_now()
    logging.info("Starting daily web scraping and preprocessing (%s to %s)." % (start_time, end_time))
    # Scrape SVT Play 
    urls_file = scraper.scrape_genres(GENRES)

    #if SAVE_TO_DB: # if database is enabled 
    
    shows = video_repo.get_shows()
    for show in shows: 
        seasons = video_repo.get_show_seasons(show)
        for season in seasons: 
            videos = video_repo.find_by_show_and_season(show, season)
            for video in videos: 
                now = datetime.now()
                if now < end_time: 
                    try: 
                        preprocess_video(video)
                    except Exception as err
                        logging.error(err)
                else: 
                    logging.info("Finished preprocessing for today at: %s" % now)
                    return 

    #else: 
    #   print(output) possibly loop through all the urls in the output from webscraper


def start_schedule():
    start_time, end_time, now = __get_start_end_time_now()
    if start_time < now and now < end_time:
        do_work()
    
    schedule.every().day.at(START_WORK).do(do_work)
    while True:
        schedule.run_pending()
        time.sleep(PENDING_CHECK_INTERVAL)

