""" 
    video_repo.py is a database interface to all videos managed by the program.

    API: 

    *   insert(video)
    
    *   find_all()
    *   find_all_not_dl(): 
    *   find_all_dl()
    *   find_by_url(url)
    *   find_by_urls(urls)
    *   find_by_file(videoFileName)
    *   find_by_show(show)
    *   find_by_show_not_dl(show)
    *   find_by_show_and_season(show, season)
    *   find_by_show_and_season_not_dl(show, season)
    *   find_by_show_season_episode(show, season, episode)
    *   get_shows()
    *   get_show_seasons(show):


    *   find_by_presence_of_key(key)
    *   find_all_with_intro_prediction()
    *   find_all_with_intro_annotation():

    *   save_after_download(url, mp4_fullpath)
    *   set_downloaded_flag(url, flag)
    *   change_fullpath(file, fullpath)
    *   set_data_by_file(file, key, data):
    *   set_data_by_url(url, key, data):

    *   set_intro_prediction(url, start, end)
    *   set_intro_annotation(url, start, end)
    
    *   delete_by_file(videoFileName):
    *   delete_by_url(url):
    *   delete_show(show)

"""

import pymongo
import json
import os 
from pathlib import Path

import db.show_repo as show_repo

class Video:
    """ Class containing video information """

    def __init__(self, show="", title="", season=0, episode=0, url="", downloaded=False):
        self.show = show.lower() # save as lower case
        self.title = title
        self.season = season
        self.episode = episode 
        self.url = url
        self.downloaded = downloaded
        
    def __repr__(self):
        return "Video('{}', '{}', {}, {}, '{}', {})".format(self.show, self.title, self.season, self.episode, self.url, self.downloaded)

    def setDwonloaded(self, flag):
        self.downloaded = flag

    def hasDownloaded(self):
        return self.downloaded 

    @property
    def filename(self):
        return '{}.s{:02}e{:02}'.format(self.show, self.season, self.episode)


INTRO_ANNOTATION_KEY    = 'intro_ann'
INTRO_PREDICTION_KEY    = 'intro_pre'
PREINTRO_ANNOTATION_KEY = 'prei_ann'
PREVIOUS_ANNOTATION_KEY = 'prev_ann'
URL_KEY                 = 'url'
SHOW_KEY                = 'show'
SHOW_ID_KEY             = 'showId'
TITLE_KEY               = 'title'
SEASON_KEY              = 's'
EPISODE_KEY             = 'e'
DOWNLOADED_KEY          = 'dl'
PREPROCESSED_KEY        = 'preproc'
FULL_PATH_KEY           = 'fullpath'
FILE_KEY                = 'file'
SEGMENTS_KEY            = 'segs'


secret = None
with open(".secret.json") as json_file:
    secret = json.load(json_file)
dbName = secret['dbname']
url = secret['url']
mongoClient = pymongo.MongoClient(url)
db = mongoClient[dbName]
videoCollection = db["videos"]


def insert(video):
    if not isinstance(video, Video):
        raise TypeError('Inappropriate type: {}, Expected: {}.'.format(type(video), type(Video)))
    if find_by_url(video.url) is not None: 
        return None
    return videoCollection.insert_one({
        SHOW_KEY: video.show,
        SHOW_ID_KEY: show_repo.get_show_from_dl_url(video.url),
        TITLE_KEY: video.title, 
        SEASON_KEY: video.season, 
        EPISODE_KEY: video.episode, 
        URL_KEY: video.url, 
        DOWNLOADED_KEY: video.downloaded,
        INTRO_ANNOTATION_KEY: False,
        INTRO_PREDICTION_KEY: False 
    }).inserted_id

def find_all():
    return list(videoCollection.find())

def find_all_not_preprocessed():
    return list(videoCollection.find({PREPROCESSED_KEY: { "$ne": True }}))  # Not True or does not exists

def find_by_url(url):
    return videoCollection.find_one({ URL_KEY: url})

def find_by_urls(urls):
    return list(videoCollection.find({ URL_KEY: { "$in": urls } }))

def find_by_file(filename):
    return videoCollection.find_one({FILE_KEY: filename})

""" Example: queryArray = [ {SHOW_ID_KEY: show_id}, {SEASON_KEY: season} ] """
def find_by_many(queryArray):
    return list( videoCollection.find({ "$and": queryArray }))


def find_by_show(show):
    return list(videoCollection.find({SHOW_KEY: show}))
    
def find_by_show_and_season(show, season):
    return find_by_many([{SHOW_KEY: show}, {SEASON_KEY: season}])

def find_by_show_season_episode(show, season, episode):
    return find_by_many([{SHOW_KEY: show}, {SEASON_KEY: season},  {EPISODE_KEY: episode}])
    
def find_by_presence_of_key(key):
    return list(videoCollection.find({key: {
            "$exists": True 
        }
    }))

def find_all_with_intro_prediction():
    return find_by_presence_of_key(INTRO_PREDICTION_KEY)

def find_all_with_intro_annotation():
    return find_by_presence_of_key(INTRO_ANNOTATION_KEY)

def set_many_by_url(url, KeyValuePairs):
    return videoCollection.update_one({ URL_KEY: url }, 
    {
        "$set": KeyValuePairs
    }, upsert = False).matched_count

def set_data_by_file(videoFileName, key, data):
    return videoCollection.update_one({ FILE_KEY: videoFileName }, 
    {
        "$set": { key: data }
    }, upsert = False).matched_count

def set_data_by_url(url, key, data):
    return videoCollection.update_one({ URL_KEY: url }, 
    {
        "$set": { key: data }
    }, upsert = False).matched_count

def unset_data_by_url(url, key):
     return videoCollection.update_one({ URL_KEY: url }, 
    {
        "$unset": key 
    }, upsert = False).matched_count


def __validate_int_or_float(arg):
    return isinstance(arg, int) or isinstance(arg, float)

def __assert_time_start_end(start, end):
    if not (__validate_int_or_float(start)):
        raise TypeError("start: %s" % start)
    if not (__validate_int_or_float(end)):
        raise TypeError("end: %s" % end )  

def set_intro_prediction(url, start, end):
    __assert_time_start_end(start, end)
    return set_data_by_url(url, INTRO_PREDICTION_KEY, { "start": start, "end": end } )

def set_intro_annotation(url, start, end):
    __assert_time_start_end(start, end)
    return set_data_by_url(url, INTRO_ANNOTATION_KEY, { "start": start, "end": end } )

def get_shows():
    return list(videoCollection.distinct(SHOW_KEY))

def get_show_seasons(show):
    return list(videoCollection.distinct(SEASON_KEY, {SHOW_KEY: show})) 

def delete_by_file(videoFileName):
    return videoCollection.delete_one({FILE_KEY: videoFileName}).deleted_count

def delete_by_url(url):
    return videoCollection.delete_one({URL_KEY: url}).deleted_count

def delete_by_show(show):
    return videoCollection.delete_many({SHOW_KEY: show}).deleted_count

