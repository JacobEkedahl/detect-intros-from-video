
import json

import utils.file_handler as file_handler
from annotations import annotate_intro, annotate_subtitles
from audio_extraction import video_to_pitches as a_matcher
from classifier import stats
from downloader import svtplaywrapper
from frame_matcher import video_matcher, video_to_hashes
from segmenter import scenedetector, simple_segmentor
from utils import extractor


def build_dataset():
    build_dataset_from_step("--start", "--end")
    # read from textfile
    # for each url in text file
    # download
    # merge and cut
    # segment
    # extract frames
    # remove similar frames

    # for each video in each tvseries
    # match similar frames
    # annotate segments in json of matching frames
    return 0

def build_dataset_from_step(fromStep, toStep):
    if fromStep == "--format":
        extractor.reformat_segmentation_files()
        exit()

    if fromStep == "--start":
        urls = file_handler.get_all_urls_from_temp()
        for url in urls:
            file_name = svtplaywrapper.download_video(url)
            if toStep == "--seg": #not adviced to skip this step after start (miss the urlconnection for later intro connections)
                exit()
            if file_name == None: # download or merge failed, try next video
                continue
            simple_segmentor.segment_video_with_url(file_name, url)
            annotate_intro.annotate_intro(file_name, url) # finding intro with this url from dataset
            if toStep == "--frames":
                exit()
           # video_to_hashes.save_hashes(file_name)
           # annotate_subtitles.annotate_subs_from_video(file_name) # will annotate subs
            #a_matcher.get_audio_from_video(file_name) # will annotate pitches
        if toStep == "--sim":
            exit()
        fromSim(toStep)
    elif fromStep == "--frames":
        fromFrames(toStep)
    elif fromStep == "--sim":
        fromSim(toStep)

def fromFrames(toStep):
    # find all videofiles
    video_files = file_handler.get_all_mp4_files()
    for video_file in video_files:
        #seg_file = file_handler.get_seg_file_from_video(video_file)
        #with open(seg_file) as json_file:
        #    data = json.load(json_file)
           # if "pitches" not in data["scenes"][0]:
       # a_matcher.get_audio_from_video(video_file)
           # if "intro" not in data["scenes"][0]:
        video_url = file_handler.get_url_from_file_name(video_file) #requires url to be saved in json
        annotate_intro.annotate_intro(video_file, video_url)
           # if "subtitles" not in data["scenes"][0]:
           #     annotate_subtitles.annotate_subs_from_video(video_file) # will annotate subs
       # video_to_hashes.save_hashes(video_file)
    if toStep == "--sim":
        exit()
    fromSim(toStep)

def fromSim(toStep):
    video_files = file_handler.get_all_mp4_files()
    for video_file in video_files:
        seg_file = file_handler.get_seg_file_from_video(video_file)
        video_matcher.find_all_matches(video_file)
