
import utils.file_handler as file_handler
from audio_extraction import video_to_pitches as a_matcher
from downloader import svtplaywrapper
from frame_matcher import video_matcher, video_to_hashes
from segmenter import scenedetector, simple_segmentor


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
    if fromStep == "--start":
        urls = file_handler.get_all_urls_from_temp()
        for url in urls:
            file_name = svtplaywrapper.download_video(url)
            if toStep == "--seg":	
                exit()
            simple_segmentor.segment_video(file_name)
            if toStep == "--frames":
                exit()
            video_to_hashes.save_hashes(file_name)
            if toStep == "--audio":
                exit()
            a_matcher.convert(file_name)

        if toStep == "--sim":
            exit()

        video_files = file_handler.get_all_mp4_files()
        for video_file in video_files:
            video_matcher.find_all_matches(video_file)
    elif fromStep == "--seg": ## will clean previous annotations
        # find all videofiles
        video_files = file_handler.get_all_mp4_files()
        for file in video_files:
            simple_segmentor.segment_video(file)
        fromFrames(toStep)
    elif fromStep == "--frames":
        fromFrames(toStep)
    elif fromStep == "--sim":
        fromSim(toStep)

def fromFrames(toStep):
    # find all videofiles
    video_files = file_handler.get_all_mp4_files()
    for video_file in video_files:
        video_to_hashes.save_hashes(video_file)
        a_matcher.convert(video_file)
    if toStep == "--sim":
        exit()
    for video_file in video_files:
        video_matcher.find_all_matches(video_file)

def fromSim(toStep):
    video_files = file_handler.get_all_mp4_files()
    for video_file in video_files:
        video_matcher.find_all_matches(video_file)
