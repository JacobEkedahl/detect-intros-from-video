import os
import pickle

import utils.constants as c
import utils.file_handler as file_handler


def save_pitches(video_file, pitches):
    audio_dir = file_handler.get_dir_for_audio(video_file)
    output = os.path.join(audio_dir, c.FREQ_NAME)
    with open(output, 'wb') as pitch_file:
        pickle.dump(pitches, pitch_file)

def open_pitches(video_file):
    audio_path = file_handler.get_dir_for_audio(video_file)
    audio_obj_path = os.path.join(audio_path, c.FREQ_NAME)
    with open(audio_obj_path, 'rb') as pitch_file:
        return pickle.load(pitch_file)

def get_hash(video_file):
    hash_path = file_handler.get_dir_for_frames(video_file)
    hash_obj_path = os.path.join(hash_path, c.HASH_NAME)
    with open(hash_obj_path, 'rb') as hash_file:
        return pickle.load(hash_file)

def save_hash(video_file, hash_val):
    hash_path = file_handler.get_dir_for_frames(video_file)
    hash_obj_path = os.path.join(hash_path, c.HASH_NAME)
    with open(hash_obj_path, 'wb') as hash_file:
        pickle.dump(hash_val, hash_file)
