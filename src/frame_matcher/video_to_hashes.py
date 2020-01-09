import os

import cv2
import imagehash
from PIL import Image

import utils.constants as c
import utils.file_handler as file_handler
import utils.object_handler as handler


def save_hashes(video_filename):
    video_filename = str(video_filename)
    if not file_handler.does_meta_contain_obj(c.HASH_NAME, video_filename):
        print("there is no hashfile")
        hashes = []
        video_to_hashes(video_filename, hashes)
        handler.save_obj_in_meta(c.HASH_NAME,hashes, video_filename)
    else:
        print("hashfile already exists")

#Will override all files already existing in this folder
def video_to_hashes(video_filename, hashes):
    vidcap = cv2.VideoCapture(video_filename)
    sec = 0
    frameRate = c.SEC_PER_FRAME #//it will capture image in each 0.5 second
    count=1
    success = get_hash(vidcap, sec, count, video_filename, hashes)
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success = get_hash(vidcap, sec, count, video_filename, hashes)
    vidcap.release()


def get_hash(vidcap, sec, count, video_filename, hashes):
    vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
    hasFrames,image = vidcap.read()

    if hasFrames:
        image = cv2.resize(image,(c.IMAGE_WIDTH,c.IMAGE_HEIGHT))
        hash_img = imagehash.average_hash(Image.fromarray(image))
        hashes.append({"hash": hash_img, "count": count, "sec": sec})
    return hasFrames
