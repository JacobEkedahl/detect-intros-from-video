import cv2

import utils.constants as c
import utils.file_handler as file_handler

from . import frame_cleaner


def video_to_frames_check(video_filename):
    video_filename = str(video_filename)
    if file_handler.is_dir_for_frames_empty(video_filename):
        print("there is no files")
        video_to_frames(video_filename)
    else:
        print("files already exists")

#Will override all files already existing in this folder
def video_to_frames(video_filename):
    vidcap = cv2.VideoCapture(video_filename)
    sec = 0
    frameRate = c.SEC_PER_FRAME #//it will capture image in each 0.5 second
    count=1
    success = save_frame(vidcap, sec, count, video_filename)
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success = save_frame(vidcap, sec, count, video_filename)

def save_frame(vidcap, sec, count, video_filename):
    file_name = file_handler.get_file_name_frame(video_filename, sec, count)
    vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
    hasFrames,image = vidcap.read()

    if hasFrames:
        image = cv2.resize(image,(c.IMAGE_WIDTH,c.IMAGE_HEIGHT))
        cv2.imwrite(file_name, image)     # save frame as JPG file
    return hasFrames
