import os
import pickle

import utils.constants as c
import utils.file_handler as file_handler


def save_obj_in_meta(obj_type, obj, video_file):
    with open(get_output(video_file, obj_type), 'wb') as obj_file:
        pickle.dump(obj, obj_file)

def open_obj_from_meta(obj_type, video_file):
    with open(get_output(video_file, obj_type), 'rb') as hash_file:
        return pickle.load(hash_file)

def get_output(video_file, obj_type):
    dir = file_handler.get_dir_for_meta(video_file)
    return os.path.join(dir, obj_type)
