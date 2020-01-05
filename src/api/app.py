from flask import Flask 

import sys
import os 

import db.video_repo as video_repo 
from bson import ObjectId

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World" # Should return api description or readme

@app.route('/api:video/<string:url>', methods=["GET"])
def get_video(url):
    video = video_repo.find_by_url("https://www.svtplay.se/video/24136938/exit/exit-avsnitt-1")
    video.pop("_id")
    return video

@app.route('/api:prediction/<string:url>', methods=["GET"])
def get_prediction(url):
    return url

@app.route('/api:annotation/<string:url>', methods=["GET"])
def get_annotation(url):
    print("lol")

def start():
    app.run(debug=True)

