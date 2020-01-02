import logging 

import time
import schedule
import multiprocessing

from utils import constants, file_handler 
import db.video_repo as video_repo 
import downloader.scrapesvt as scraper 
import downloader.download_video as dl 

from segmenter import blackdetector, scenedetector, simple_segmentor

from annotations import annotate_black

import annotations.annotate_meta as meta
import annotations.annotate as annotate 

HAS_STARTED = False 
GENRES = constants.VIDEO_GENRES
APPLY_BLACK_DETECTION = constants.APPLY_BLACK_DETECTION
APPLY_SCENE_DETECTION = constants.APPLY_SCENE_DETECTION


SAVE_TO_FILE = constants.SAVE_TO_FILE
SAVE_TO_DB = constants.SAVE_TO_DB

DELETE_VIDEO_AFTER_EXTRACTION = constants.DELETE_VIDEO_AFTER_EXTRACTION


CPU_COUNT = multiprocessing.cpu_count()
processedUrls = []




def __handle_season_videos(videos):
    # Downloads all previously not downloaded videos 
    any_video_was_downlaoded = False 
    for video in videos: 
        if not video['downloaded']:
            # if a video was not previously downloaded --> extract video features
            videofile, subsfile = dl.download(video['url'])
            if videofile:
                print("Download completed: %s " % videofile)
            else: 
                logging.warn("%s skipped", video['url'])
                continue 

            segments = simple_segmentor.segment_video(videofile)

            if APPLY_BLACK_DETECTION: 
                blackSequences, blackFrames = blackdetector.detect_blackness(videofile)
                segments = annotate_black.annotate_black_frames(segments, blackdetector.FRAME_KEY, blackFrames)
                segments = annotate_black.annotate_black_sequences(segments, blackdetector.SEQUENCE_KEY, blackSequences)
                # Combines previous annotations into one 
                segments = annotate_black.combine_annotation_into(segments, "black", blackdetector.SEQUENCE_KEY, blackdetector.FRAME_KEY, True)
                if SAVE_TO_FILE:
                    file_handler.save_to_file(videofile, simple_segmentor.SCENES_KEY, segments)
                

                for blackFrame in blackFrames:
                    print(blackFrame)    
                for blackSequence in blackSequences: 
                    print(blackSequence)
                
            if APPLY_SCENE_DETECTION:
                exit()
                scenes = scenedetector.detect_scenes(videofile)
                  # meta.annotate_meta_data(scenes, scenedetector.DATA_KEY, videofile)
                # annotate here 
                for scene in scenes: 
                    print(scene)
                

            
           
  
                

            any_video_was_downlaoded = True 
                
            exit()
            # Delete video 
            #if DELETE_VIDEO_AFTER_EXTRACTION:
            #    print("Delete video")
        else:
            print("%s %02d %02d was downloaded before" % (video['show'], video['season'], video['episode']))


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
            __handle_season_videos(videos)

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

