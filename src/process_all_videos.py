import logging 

import time
import schedule
import multiprocessing

from utils import constants, file_handler 
import db.video_repo as video_repo 
import downloader.scrapesvt as scraper 
import downloader.download_video as dl 

from segmenter import blackdetector, scenedetector, simple_segmentor
from annotations import annotate_black, annotate_scenes,annotate, annotate_intro

from frame_matcher import video_to_hashes, video_matcher

HAS_STARTED = False 
GENRES = constants.VIDEO_GENRES
APPLY_BLACK_DETECTION = constants.APPLY_BLACK_DETECTION
APPLY_SCENE_DETECTION = constants.APPLY_SCENE_DETECTION


SAVE_TO_FILE = constants.SAVE_TO_FILE
SAVE_TO_DB = constants.SAVE_TO_DB

DELETE_VIDEO_AFTER_EXTRACTION = constants.DELETE_VIDEO_AFTER_EXTRACTION


CPU_COUNT = multiprocessing.cpu_count()
processedUrls = []


def process_video(video):
    if not video['downloaded']:
        videofile, subsfile = dl.download(video[video_repo.URL_KEY])
        if videofile:
            print("Download completed: %s " % videofile)
        else: 
            logging.warn("%s skipped", video[video_repo.URL_KEY])
            return # Optionally raise an exception ?

        segments = simple_segmentor.segment_video(videofile)

        if APPLY_BLACK_DETECTION: 
            blackSequences, blackFrames = blackdetector.detect_blackness(videofile)
            segments = annotate_black.annotate_black_frames(segments, blackdetector.FRAME_KEY, blackFrames)
            segments = annotate_black.annotate_black_sequences(segments, blackdetector.SEQUENCE_KEY, blackSequences)
            segments = annotate_black.combine_annotation_into(segments, "black", blackdetector.SEQUENCE_KEY, blackdetector.FRAME_KEY, True)
        
        if APPLY_SCENE_DETECTION:
            scenes = scenedetector.detect_scenes(videofile)
            segments = annotate_scenes.annotate_detected_scenes(segments, scenes, scenedetector.DATA_KEY)

        if video_repo.INTRO_ANNOTATION_KEY in video: 
            intro = video[video_repo.INTRO_ANNOTATION_KEY]
            segments = annotate_intro.apply_annotated_intro_on_segments(video[video_repo.URL_KEY], segments, intro)
        

        exit()

        print("video to hashesh")
        video_to_hashes.save_hashes(videofile)
        print("video to hashes done")
        video_matcher.find_all_matches(videofile)
        print("video matcher done")

        exit()
        if SAVE_TO_FILE:
            file_handler.save_to_file(videofile, simple_segmentor.SCENES_KEY, segments)
            
        if SAVE_TO_DB:
            print("saving changes to db...")



def handle_Season_videos(videos):
    # Downloads all previously not downloaded videos 
    any_video_was_downlaoded = False 
    for video in videos: 
        process_video(video)


    # If there are more seasons but only one video comparison should still be made

    # if a video was downloaded and there are more than one --> perform video comparison 
    if any_video_was_downlaoded: 
        print("Do video comparison")
        for video in videos: 
            print("%s %s %s %s" %(video['show'], video['season'], video['episode'], video['downloaded']))



def __work():
    # Scrape svtplay for new content 
    #for genre in GENRES: 
    #    scraper.scrape_genre(genre)


    print("CPU COUNT: %d" % CPU_COUNT)

    # Iterate through all videos sorted by show and season 
    shows = video_repo.get_shows()
    for show in shows: 
        seasons = video_repo.get_show_seasons(show)
        for season in seasons: 
            videos = video_repo.find_by_show_and_season(show, season)
            handle_Season_videos(videos)

def start():
    
    global HAS_STARTED 
    if HAS_STARTED:
        return 
    HAS_STARTED = True 
    print("Starting...")

    # if the db is empty a work session is started immedietly
    if (len(video_repo.find_all()) == 0):
        __work()

    __work()

    #schedule.every(1).minutes.do(__work)

    while True:
        schedule.run_pending()
        time.sleep(1)

