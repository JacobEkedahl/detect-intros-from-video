from annotations import annotate_meta
from utils import file_handler

from . import prob_calculator


def annotate_stats(video_file):
    other_videos = file_handler.get_other_videos_in_series(video_file)
    other_intros = file_handler.get_intros_from_videos(other_videos)
    guessed_intro = prob_calculator.guess_intro(other_intros)
    annotate_meta.annotate_meta_data(guessed_intro, "GUESS", video_file)
