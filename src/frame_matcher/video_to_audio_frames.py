import os
import subprocess

import imageio_ffmpeg as ffmpeg

from utils import constants, file_handler

from . import convert_audio_to_img


def audio_to_frames(video_file_path):
    if file_handler.is_dir_for_audio_empty(video_file_path):
        print("there is no audio frames")
        get_audio_from_video(video_file_path)
    else:
        print("files already exists")

def get_audio_from_video(video_file_path):
    base_dir = file_handler.get_dir_for_audio(video_file_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    output = os.path.join(base_dir, "audio.wav")
    command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", video_file_path, "-ab", "160k", "-ac", "1", "-ar", "44100", "-vn", "-y",  output]
    subprocess.call(command, shell=True) 
    dir_to_audio = os.path.dirname(output)
    split_into_parts(dir_to_audio, output)
    os.remove(output)
    convert_to_images(dir_to_audio)
    remove_all_audio(dir_to_audio)

def split_into_parts(dir_to_audio, path_to_audio):
    command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", path_to_audio, "-f", "segment", "-segment_time", constants.AUDIO_SIZE_SPLITS, "-c", "copy", os.path.join(dir_to_audio,"out-%03d.wav")]
    subprocess.call(command, shell=True) 

def convert_to_images(dir_to_audio):
    files = file_handler.get_all_files_by_type(dir_to_audio, "wav")
    for file_path in files:
        convert_audio_to_img.convert_audio_to_spec(file_path)
        
def remove_all_audio(dir_to_audio):
    audio_files = file_handler.get_all_files_by_type(dir_to_audio, "wav")
    for audio in audio_files:
        os.remove(audio)
