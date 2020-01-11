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
WAS_DL = video_repo.DOWNLOADED_KEY
FILE = video_repo.FILE_KEY
PREPROCESSED = video_repo.PREPROCESSED_KEY
SEGMENTS = video_repo.SEGMENTS_KEY

def __extract_frame_hashes(video):
    start = datetime.now()
    video_to_hashes.save_hashes(video[PATH]) 
    logging.info("frame-hash extraction complete, time taken: %s" % (datetime.now()  - start))


def __annotate_intro(video, segments):
    start = datetime.now()
    intro = video[video_repo.INTRO_ANNOTATION_KEY]
    annotate_intro.apply_annotated_intro_on_segments(segments, intro)
    logging.info("intro annotation complete (%s), time taken: %s" % (intro, datetime.now()  - start))


def __annotate_detected_scene(video, segments):
    start = datetime.now()
    scenes = scenedetector.detect_scenes(video[PATH])
    annotate_scenes.annotate_detected_scenes(segments, scenes, scenedetector.DATA_KEY)
    logging.info("scenedetection complete, %d scenes, time taken: %s" % (len(scenes), datetime.now()  - start))


def __annotate_detected_blackness(video, segments):
    start = datetime.now()
    blackSequences, blackFrames = blackdetector.detect_blackness(video[PATH])
    annotate_black.annotate_black_frames(segments, blackdetector.FRAME_KEY, blackFrames)
    annotate_black.annotate_black_sequences(segments, blackdetector.SEQUENCE_KEY, blackSequences)
    annotate_black.combine_annotation_into(segments, "black", blackdetector.SEQUENCE_KEY, blackSequences, blackdetector.FRAME_KEY, blackFrames, False)
    logging.info("blackdetection complete, %d black frames, %d black sequence, time taken: %s" % (len(blackFrames), len(blackSequences), datetime.now()  - start))


def __download_video(video):
    try: 
        start = datetime.now()
        videofile = dl.download_video(video[URL])
        if videofile is not None: 
            video[WAS_DL] = True
            video[PATH] = videofile 
            video[FILE] = os.path.basename(videofile)
            changes = { 
                WAS_DL: video[WAS_DL], 
                PATH: video[PATH], 
                FILE:  video[FILE] 
            } # save meta
            video_repo.set_many_by_url(video[URL], changes)
            logging.info("download complete: %s, time taken: %s" % (videofile, datetime.now()  - start))
            return True 
        else:
            logging.error("Could not find video file associated with: %s" % video[URL])
            return False 
    except Exception as e: 
        logging.exception(e) 
        logging.error("failed to download: %s" % video[URL])
        return False 


def __delete_video_files(video):
    subs = video[PATH].replace("-converted.mp4", ".srt")
    if os.path.exists(subs):
        os.remove(subs)
    if os.path.exists(video[PATH]):
        os.remove(video[PATH])


def preprocess_video(video):

    # One could query the video again here if there is a desire to allow for concurrent preprocessing on multiple servers. 
    # It would then check if the download or preprocessing has already been done before continuing.

    initStart = datetime.now()
    logging.info("\n---\nPreprocessing of %s started at: %s", video[URL], initStart)
    # if video was not downloaded --> download
    if not video[WAS_DL]:
        result = __download_video(video)
        if result == False:
            return result # download failure 
   
    segments = simple_segmentor.get_video_segments(video[PATH]) # factory method for creating or getting previously created segments 

    if video_repo.INTRO_ANNOTATION_KEY in video:  
        __annotate_intro(video, segments)

    if APPLY_BLACK_DETECTION: 
        __annotate_detected_blackness(video, segments)

    if APPLY_SCENE_DETECTION:
        __annotate_detected_scene(video, segments)

    __extract_frame_hashes(video)

    if DELETE_VIDEO_FILES_AFTER_EXTRACTION:
        __delete_video_files(video)

    if len(segments) <= 0:
        raise ValueError("Something went wrong with the segmentation.")

    video[SEGMENTS] = segments 
    video[PREPROCESSED] = True 

    if SAVE_TO_FILE:
        file_handler.save_to_video_file(video[PATH], simple_segmentor.SCENES_KEY, segments)
        file_handler.save_to_video_file(video[PATH], URL, video[URL])

    # Mark as preprocessed
    video_repo.set_many_by_url(video[URL], {
        # Could save segments here if desired
        PREPROCESSED: video[PREPROCESSED] 
    })

    logging.info("preprocessing complete, time taken: %s" % (datetime.now() - initStart))
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

    
def __do_timed__work():
    
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

    logging.basicConfig(filename='preprocess.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    start_time, end_time, now = __get_start_end_time_now()
    logging.info("Preprocess schedule started between %s and %s." %(start_time, end_time))
    if start_time < now and now < end_time:
        __do_timed__work()
    schedule.every().day.at(START_WORK).do(__do_timed__work)
    while True:
        schedule.run_pending()
        time.sleep(PENDING_CHECK_INTERVAL)

