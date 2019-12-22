
import utils.file_handler as file_handler
from downloader import svtplaywrapper
from frame_matcher import frame_cleaner, video_matcher, video_to_frames
from segmenter import scenedetector


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
            scenedetector.segment_video(file_name)

            if toStep == "--frames":
                exit()
            video_to_frames.video_to_frames_check(file_name)
            #frame_cleaner.remove_similar_frames(file_name)

        if toStep == "--sim":
            exit()

        video_files = file_handler.get_all_mp4_files()
        for video_file in video_files:
            matches = video_matcher.find_all_matches(video_file)
    elif fromStep == "--frames":
        # find all videofiles
        video_files = file_handler.get_all_mp4_files()
        for video_file in video_files:
            video_to_frames.video_to_frames_check(video_file)
            #frame_cleaner.remove_similar_frames(video_file)

        if toStep == "--sim":
            exit()

        for video_file in video_files:
            matches = video_matcher.find_all_matches(video_file)
    elif fromStep == "--sim":
        video_files = file_handler.get_all_mp4_files()
        for video_file in video_files:
            matches = video_matcher.find_all_matches(video_file)
