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
PENDING_CHECK_INTERVAL = 10

GENRES = constants.VIDEO_GENRES
APPLY_BLACK_DETECTION = constants.APPLY_BLACK_DETECTION
APPLY_SCENE_DETECTION = constants.APPLY_SCENE_DETECTION
DELETE_VIDEO_FILES_AFTER_EXTRACTION = constants.DELETE_VIDEO_AFTER_EXTRACTION
SAVE_TO_FILE = constants.SAVE_TO_FILE
URL = video_repo.URL_KEY
PATH = video_repo.FULL_PATH_KEY
DL = video_repo.DOWNLOADED_KEY
FILE = video_repo.FILE_KEY
PREPROCESSED = video_repo.PREPROCESSED_KEY
SEGMENTS = video_repo.SEGMENTS_KEY

def preprocess_video(video):

    start = datetime.now()
    logging.info("\n---\nPreprocessing of %s started at: %s", video[URL], start)
    # if video was not downloaded --> download
    if not video[DL]:
        try: 
            videofile = dl.download_video(video[URL])
            if videofile is not None: 
                video[DL] = True
                video[PATH] = videofile 
                video[FILE] = os.path.basename(videofile)
                changes = { 
                    DL: video[DL], 
                    PATH: video[PATH], 
                    FILE:  video[FILE] 
                } # save meta
                video_repo.set_many_by_url(video[URL], changes)
                logging.info("Download complete: %s, time taken: %s" % (videofile, datetime.now()  - start))
            else:
                logging.error("Could not find video file associated with: %s" % video[URL])
                return False 
        except Exception as e: 
            logging.exception(e) 
            logging.error("failed to download: %s" % video[URL])
            return False 
    else:
        videofile = video[video_repo.FULL_PATH_KEY]

    # factory method for creating or getting previously created segments 
    segments = simple_segmentor.get_video_segments(videofile)
    file_handler.save_to_video_file(videofile, URL, video[URL])
    
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

    # Extrach frame hashes from videofile     
    start = datetime.now()
    video_to_hashes.save_hashes(videofile) 
    logging.info("hash extraction complete, time taken: %s" % (datetime.now()  - start))

    if DELETE_VIDEO_FILES_AFTER_EXTRACTION:
        subs = video[PATH].replace("-converted.mp4", ".srt")
        if os.path.exists(subs):
            os.remove(subs)
        if os.path.exists(video[PATH]):
            os.remove(video[PATH])

    video[SEGMENTS] = segments 
    video[PREPROCESSED] = True 

    if SAVE_TO_FILE:
        file_handler.save_to_video_file(videofile, simple_segmentor.SCENES_KEY, segments)

    # Mark as preprocessed
    video_repo.set_many_by_url(video[URL], {
        # Could save segments here if desired
        PREPROCESSED: video[PREPROCESSED] 
    })

    logging.info("Saved changes for: %s" % video[URL])
    return True 


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

    # TODO: if the dataset is zero we import everything from the dataset to the database. Otherwise we assume that this has already been done ???

    start_time, end_time, now = __get_start_end_time_now()
    logging.info("\n---\nStarting daily web scraping and preprocessing (%s to %s).\n---" % (start_time, end_time))
    scraper.scrape_genres(GENRES)

    # Keep preprocessing videos until end time is exceeded. 
    # Any failed preprocessed are attempted again in the next iteration.  
    count_success = 0
    count_failure = 0


    while datetime.now() < end_time: 
        videos = video_repo.find_all_not_preprocessed()
        if len(videos) == 0:
            break 
        for video in videos: 
            if datetime.now() > end_time:
                break 
            if not (PREPROCESSED in video and video[PREPROCESSED]):
                try: 
                    result = preprocess_video(video)
                    if not result: 
                        logging.error("Failed to preprocess: %s" % video[URL])
                        count_failure = count_failure + 1 
                    else: 
                        count_success = count_success + 1 
                except Exception as e:
                    logging.exception(e)

    logging.info("Finished preprocessing session at: %s\nSuccess: %d\nFailure: %d" % (datetime.now(), count_success, count_failure))
            

def start_schedule():
    start_time, end_time, now = __get_start_end_time_now()
    logging.info("Preprocess schedule started between %s and %s." %(start_time, end_time))
    if start_time < now and now < end_time:
        do_work()
    schedule.every().day.at(START_WORK).do(do_work)
    while True:
        schedule.run_pending()
        time.sleep(PENDING_CHECK_INTERVAL)

