import json

from annotations import scene_annotation
from segmenter import simple_segmentor

from . import file_handler


def remove_annotations(annotation):
    all_videos = file_handler.get_all_mp4_files()
    for video in all_videos:
        seg_file = file_handler.get_seg_file_from_video(video)
        scene_annotation.delete_annotation(annotation, seg_file)

def remove_annotation_from_series(annotation, serie_name):
    all_videos = file_handler.get_all_mp4_files()
    startRemoving = False
    print(serie_name)
    for video in all_videos:
        if serie_name in video and startRemoving == False:
            startRemoving = True
        if startRemoving:
            print("removing..")
            seg_file = file_handler.get_seg_file_from_video(video)
            scene_annotation.delete_annotation(annotation, seg_file)

def format_file(video_file):
    seg_file = file_handler.get_seg_file_from_video(video_file)
    with open(seg_file) as json_file:
        data = json.load(json_file)
        url = data['url']
        simple_segmentor.segment_video_with_url(video_file, url)
        
def reformat_segmentation_files():
    files = file_handler.get_all_mp4_files()
    for video_file in files:
        seg_file = file_handler.get_seg_file_from_video(video_file)
        with open(seg_file) as json_file:
            data = json.load(json_file)
            url = data['url']
            simple_segmentor.segment_video_with_url(video_file, url)
