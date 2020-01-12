from flask import Flask, request, jsonify, render_template, abort
import json 
import logging 

import db.video_repo as video_repo 
import predicting
import rebuild

app = Flask(__name__)
DEBUG_ON = False 

INTERNAL_SERVER_ERROR = 500
BAD_REQUEST = 400
NOT_FOUND = 404
OK = 200

QUERY_REQUEST_FAILURE_MSG   = "Failed to perform query request."
NO_MATCHING_URL             = "No video has that url."
NO_URL_FOUND_MSG            = "No url found in body."
INVALID_START_END_MSG       = "Start and end must be denoted in seconds as a float or integer."
INTRO_ANN_MSG               = "Body must contain url, start and stop keys."
NO_SHOW_WITH_NAME           = "No show found with that name."

INTRO_PRED_KEY = "introPrediction"
INTRO_ANN_KEY  = "introAnnotation"

URL_DB = video_repo.URL_KEY
INTRO_ANN_DB = video_repo.INTRO_ANNOTATION_KEY
INTRO_PRED_DB = video_repo.INTRO_PREDICTION_KEY
DOWNLOADED_DB = video_repo.INTRO_PREDICTION_KEY
DOWNLOADED_DB = video_repo.DOWNLOADED_KEY


def __format_video(video):
    video.pop("_id")
    video["season"] = video.pop(video_repo.SEASON_KEY)
    video["episode"] = video.pop(video_repo.EPISODE_KEY)
    if video_repo.FULL_PATH_KEY in video: 
        video.pop(video_repo.FULL_PATH_KEY)
    if video_repo.FILE_KEY in video:    
        video.pop(video_repo.FILE_KEY)
    if video_repo.PREPROCESSED_KEY in video: 
        video["preprocessed"] = video.pop(video_repo.PREPROCESSED_KEY)
    else:
        video["preprocessed"] = False 
    if DOWNLOADED_DB in video:
        video["downloaded"] = video.pop(DOWNLOADED_DB)
    else: 
        video["downloaded"] = False 
    if INTRO_ANN_DB in video:
        video[INTRO_ANN_KEY] = video.pop(INTRO_ANN_DB)
    else: 
        video[INTRO_ANN_KEY] = None 
    if INTRO_PRED_DB in video:
        video[INTRO_PRED_KEY] = video.pop(INTRO_PRED_DB)
    else: 
        video[INTRO_PRED_KEY] = None 


def __format_videos(videos):
    for v in videos:
        __format_video(v)
    return { i : videos[i] for i in range(0, len(videos) ) }


def __response(code, msg):
    return json.dumps(msg), code, {'ContentType':'application/json'} 

def __success_response():
    return __response(OK, {"success": True })


@app.route("/")
def index():
    return "Videos" # TODO: Add resource description 


@app.route('/videos', methods=['GET'])
def query_videos():
    
    queries = []
    if "url" in request.args: 
        queries.append({video_repo.URL_KEY: request.args["url"]})
    if "show_id" in request.args: 
        queries.append({video_repo.SHOW_ID_KEY: request.args["show_id"]})
    if "show" in request.args: 
        queries.append({video_repo.SHOW_KEY: request.args["show"]})
    if "season" in request.args: 
        queries.append({video_repo.SEASON_KEY: int(request.args["season"])})
    if "episode" in request.args: 
        queries.append({video_repo.EPISODE_KEY: int(request.args["episode"])})
    if "title" in request.args: 
        queries.append({video_repo.TITLE_KEY: int(request.args["title"])})

    # Operators 
    if "page" in request.args:
        page = request.args["page"]
    
    if "limit" in request.args: 
        limit = request.args["limit"]


    try: 
        videos = video_repo.find_by_many(queries)
        return __format_videos(videos)
    except Exception as e: 
        logging.exception(e)
        return __response(INTERNAL_SERVER_ERROR, {"success": False, "message": QUERY_REQUEST_FAILURE_MSG})




@app.route('/videos/set/annotation/intro', methods=["POST"])
def set_annotation():
    try: 
        data = request.json
        if "url" in data and "start" in data and "end" in data: 
            start = data["start"]
            end = data["end"]
            url = data["url"]
            try:  
                if not (isinstance(start, int) or isinstance(start, float)) or not (isinstance(end, int) or isinstance(end, float)):
                    return __response(BAD_REQUEST, {"success": False, "message": INVALID_START_END_MSG})
                updated = video_repo.set_intro_annotation(url, start, end)
                if updated:
                    return __success_response()
                return __response(NOT_FOUND, {"success": False, "message": NO_URL_FOUND_MSG})
            except Exception as e:
                logging.exception(e)
                return __response(INTERNAL_SERVER_ERROR, {"success": False, "message": QUERY_REQUEST_FAILURE_MSG})

        return __response(BAD_REQUEST, {"success": False, "message": INTRO_ANN_MSG})
    except Exception as e: 
        return __response(BAD_REQUEST, {"success": False, "message": str(e)})


@app.route('/videos/get/prediction/intro', methods=['GET', 'POST'])
def get_video_prediction():
    print("hello???")
    try: 
        data = request.json
        if "url" in data: 
            try: 
                video = video_repo.find_by_url(data[URL_DB])
                if video is not None:
                    if INTRO_ANN_DB in video and video[INTRO_ANN_DB] is not None: 
                        return __response(OK, {
                            "intro": video[INTRO_ANN_DB],
                            "type": INTRO_ANN_KEY
                        })
                    return __response(OK, {
                        "intro": predicting.get_video_prediction(video),
                        "type": INTRO_PRED_KEY
                    })
                return __response(NOT_FOUND, {"success": False, "message": NO_MATCHING_URL})
            except Exception as e:
                logging.exception(e)
                return __response(INTERNAL_SERVER_ERROR, {"success": False, "message": QUERY_REQUEST_FAILURE_MSG})

        return __response(BAD_REQUEST, {"success": False, "message": NO_URL_FOUND_MSG})
    except Exception as e: 
        return __response(BAD_REQUEST, {"success": False, "message": str(e)})


@app.route('/videos/rebuild', methods=['GET', 'POST'])
def do_build():
    rebuild.start()
    return __response(OK, {"success": True})


def start():
    logging.basicConfig(filename='api.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)
    app.run(debug=DEBUG_ON, threaded=True)

    