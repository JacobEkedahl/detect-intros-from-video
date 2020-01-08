import logging 
import time 
from datetime import datetime, date
from db import video_repo
from utils import time_handler
from frame_matcher import video_matcher
import preprocessing
import hmm

SHOW_DB = video_repo.SHOW_KEY
SEASON_DB = video_repo.SEASON_KEY
EPISODE_DB = video_repo.EPISODE_KEY
URL_DB = video_repo.URL_KEY
PATH_DB = video_repo.FULL_PATH_KEY

ANN_INTRO_DB = video_repo.INTRO_ANNOTATION_KEY

PREPROCESSED_DB = video_repo.PREPROCESSED_KEY
INTRO_ANNOTATION_DB = video_repo.INTRO_ANNOTATION_KEY
INTRO_PREDICTION_DB = video_repo.INTRO_PREDICTION_KEY

START = "start"
END = "end"


def __get_intro_annotation(video):
    if INTRO_ANNOTATION_DB in video: 
        return video[INTRO_ANNOTATION_DB]
    return None 

# Returns a list of adjacent videos to the input-video
def __find_adjacent_videos(inputVideo):

    videos = video_repo.find_by_show_and_season(inputVideo[SHOW_DB], inputVideo[SEASON_DB])
    count = 0
    for video in videos:
        if video[URL_DB] == inputVideo[URL_DB]:
            index = count 
        count = count + 1 
    min = index - 2
    if min < 0:
        min = 0
    max = index + 3
    if max >= len(videos):
        max = len(videos)
    resultList = []
    for i in range(min, max):    
        resultList.append(videos[i])
    return resultList        


def __compare_video(video):
    start = datetime.now()
    video_matcher.find_all_matches(video[PATH_DB])
    logging.info("Video comparison complete, time taken: %s" % (datetime.now()  - start))


def __make_time_interval_human_readable(video):
    if not ANN_INTRO_DB in video:
        return {}
    timeInterval = video[ANN_INTRO_DB]
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
    predictions = hmm.get_prediction(video[PATH_DB])
    logging.info("prediction complete, time taken %s" % (datetime.now()  - start))
    return predictions 


def get_video_prediction(targetVideo):
    count_success = 0
    count_failure = 0
    for video in __find_adjacent_videos(targetVideo):
        if not (PREPROCESSED_DB in video and video[PREPROCESSED_DB]):
            try: 
                result = preprocessing.preprocess_video(video)
                if not result: 
                    logging.error("Failed to preprocess: %s" % video[URL_DB])
                    count_failure = count_failure + 1 
                else: 
                    count_success = count_success + 1 
            except Exception as e:
                logging.exception(e)
                count_failure = count_failure + 1
        if targetVideo[URL_DB] == video[URL_DB]:
            targetVideo = video 
    
    __compare_video(targetVideo)
    predictions = __predict_video(targetVideo)
    prediction = None 
    if len(predictions) > 0:
        prediction = predictions[0]
    video_repo.set_intro_prediction(targetVideo[URL_DB], prediction[START], prediction[END])

    logging.info("%s\nPrediction: %s\nAnnotation: %s\n" % (
        targetVideo[URL_DB], 
        __make_predictions_human_readable(predictions),
        __make_time_interval_human_readable(targetVideo)
    ))   

    return prediction

def get_prediction_by_url(url):
    targetVideo = video_repo.find_by_url(url)
    return get_video_prediction(targetVideo)