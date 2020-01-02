import schedule
import time
import multiprocessing

import utils.constants as constants 
import db.video_repo as video_repo 
import downloader.scrapesvt as scraper 
#import downloader.svtplaywrapper as dl 

import downloader.download_video as dl 

from segmenter import blackdetector, scenedetector, simple_segmentor

HAS_STARTED = False 
GENRES = constants.VIDEO_GENRES
APPLY_BLACK_DETECTION = constants.APPLY_BLACK_DETECTION
APPLY_SCENE_DETECTION = constants.APPLY_SCENE_DETECTION

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
        
            if videofile is None: 
                print("videofile is none...")
                exit()
            else:
                print("Download completed: %s " % videofile)

            if APPLY_BLACK_DETECTION: 
                blackSequences, blackFrames = blackdetector.detect_blackness(videofile)
                for blackSequence in blackSequences: 
                    print(blackSequence)
                
            if APPLY_SCENE_DETECTION:
                scenes = scenedetector.detect_scenes(videofile)
                for scene in scenes: 
                    print(scene)

  
                

            any_video_was_downlaoded = True 
                
            # Delete video 
            if DELETE_VIDEO_AFTER_EXTRACTION:
                print("Delete video")
        else:
            print("%s %02d %02d was downloaded before" % (video['show'], video['season'], video['episode']))


    # If there are more seasons but only one video comparison should still be made

    # if a video was downloaded and there are more than one --> perform video comparison 
    if any_video_was_downlaoded and len(videos) > 1: 
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

