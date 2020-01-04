
import json
import os

import utils.file_handler as file_handler
from annotations import annotate_intro
from downloader import svtplaywrapper
from frame_matcher import video_matcher, video_to_hashes
from segmenter import scenedetector, simple_segmentor
from utils import cleaner, constants, extractor


def build_dataset():
    build_dataset_from_step("--start", "--end", True)
    return 0

def build_dataset_from_step(fromStep, toStep, override):
    if fromStep == "--start":
        extractor.create_video_serier_file(override) # will load urls that are missing, if override take them all
        urls = file_handler.get_all_urls_from_temp()
        for url in urls:
            print("downloading: " + url)
            file_name = svtplaywrapper.download_video(url)
            if toStep == "--seg": #not adviced to skip this step after start (miss the urlconnection for later intro connections)
                exit()
            if file_name == None: # download or merge failed, try next video
                raise Exception('svtplay-dl sucks, try again')
            simple_segmentor.segment_video_with_url(file_name, url)
            annotate_intro.annotate_intro_from_url(file_name, url) # finding intro with this url from dataset
            if override or file_handler.does_meta_contain_obj(constants.HASH_NAME, file_name) == False:
                video_to_hashes.save_hashes(file_name)
        if toStep == "--sim":
            exit()
        fromSim(toStep, override)
    elif fromStep == "--frames":
        fromFrames(toStep, override)
    elif fromStep == "--sim":
        fromSim(toStep, override)


    

def fromFrames(toStep, override):
    # find all videofiles
    video_files = file_handler.get_all_mp4_files()
    for video_file in video_files:
        seg_file = file_handler.get_seg_file_from_video(video_file)
        with open(seg_file) as json_file:
            data = json.load(json_file)
            if override or "intro" not in data["scenes"][0]:
                video_url = file_handler.get_url_from_file_name(video_file) #requires url to be saved in json
                annotate_intro.annotate_intro_from_url(video_file, video_url)
               # exit()
        if override or file_handler.does_meta_contain_obj(constants.HASH_NAME, video_file) == False:
            video_to_hashes.save_hashes(video_file)
    if toStep == "--sim":
        exit()
    fromSim(toStep, override)

def fromSim(toStep, override):
    video_files = file_handler.get_all_mp4_files()
    for video_file in video_files:
        if override:
            video_matcher.find_all_matches(video_file)
        else:
            seg_file = file_handler.get_seg_file_from_video(video_file)
            with open(seg_file) as json_file:
                data = json.load(json_file)
                scenes = data['scenes']
                if 'matches' not in scenes[0]:
                    print(video_file)
                    video_matcher.find_all_matches(video_file)
