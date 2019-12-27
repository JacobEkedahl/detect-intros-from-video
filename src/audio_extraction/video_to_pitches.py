import json
import os
import subprocess

import imageio_ffmpeg as ffmpeg

from annotations import annotate_meta
from utils import constants, file_handler
from utils import object_handler as handler

from . import extract_list_of_pitches as extrator


## should probably check if pitches already have been annotated
def get_audio_from_video(video_file_path):
    video_file_path = str(video_file_path)
    base_dir = file_handler.get_dir_for_meta(video_file_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    output = os.path.join(base_dir, "audio.wav")
    exe = ffmpeg.get_ffmpeg_exe()
    command = [exe, "-i", video_file_path, "-ab", "160k", "-ac", "1", "-ar", "44100", "-vn", "-y",  output]
    subprocess.check_call(command, shell=True) 
    dir_to_audio = os.path.dirname(output)
    pitches = extrator.get_valid_pitches(output)
    annotate_meta.annotate_meta_data(pitches, constants.DESCRIPTION_PITCHES, video_file_path)
    #handler.save_obj_in_meta(constants.PITCH_NAME, pitch_sequences, video_file_path) # should probably just annotate instead of saving
    os.remove(output)
