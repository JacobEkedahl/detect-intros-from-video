import os
import subprocess

import imageio_ffmpeg as ffmpeg

from utils import constants, file_handler
from utils import object_handler as handler

from . import convert_audio_to_img
from . import extract_list_of_freq as extrator


def audio_to_frames(video_file_path):
    if file_handler.is_dir_for_audio_empty(video_file_path):
        print("there is no audio frames")
        get_audio_from_video(video_file_path)
    else:
        print("files already exists")

def get_audio_from_video(video_file_path):
    video_file_path = str(video_file_path)
    base_dir = file_handler.get_dir_for_audio(video_file_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    output = os.path.join(base_dir, "audio.wav")
    command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", video_file_path, "-ab", "160k", "-ac", "1", "-ar", "44100", "-vn", "-y",  output]
    subprocess.call(command, shell=True) 
    dir_to_audio = os.path.dirname(output)
    freq_sequences = extrator.get_db(output)
    handler.save_frequencies(video_file_path, freq_sequences)
    split_into_parts(dir_to_audio, output)
    os.remove(output)
    convert_to_images(dir_to_audio)
    remove_all_audio(dir_to_audio)
    convert_images_to_obj(dir_to_audio, video_file_path)
    remove_all_images(dir_to_audio)

def split_into_parts(dir_to_audio, path_to_audio):
    split_size = str(constants.AUDIO_SIZE_SPLITS)
    command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", path_to_audio, "-f", "segment", "-segment_time", split_size, "-c", "copy", os.path.join(dir_to_audio,"out-%03d.wav")]
    subprocess.call(command, shell=True) 

def print_max_frequency(dir_to_audio):
    files = file_handler.get_all_files_by_type(dir_to_audio, "wav")
    for file_path in files:
        extrator.print_intensity(file_path)

def convert_to_images(dir_to_audio):
    files = file_handler.get_all_files_by_type(dir_to_audio, "wav")
    for file_path in files:
        convert_audio_to_img.convert_audio_to_spec(file_path)
        
def remove_all_audio(dir_to_audio):
    audio_files = file_handler.get_all_files_by_type(dir_to_audio, "wav")
    for audio in audio_files:
        os.remove(audio)

def remove_all_images(dir_to_audio):
    image_files = file_handler.get_all_files_by_type(dir_to_audio, "jpg")
    for img in image_files:
        os.remove(img)

def convert_images_to_obj(dir_to_audio, video_file):
    frames_A = file_handler.get_audioframespath_from_video(video_file)
    frames_A.sort(key=lambda x: x.count, reverse=False)
    output = os.path.join(dir_to_audio, "audio_obj") 
    handler.save_frames(output, frames_A)
