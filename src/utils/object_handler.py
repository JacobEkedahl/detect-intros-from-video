import os
import pickle

import cv2

import utils.file_handler as file_handler


def save_frequencies(video_file, decibel):
    audio_dir = file_handler.get_dir_for_audio(video_file)
    output = os.path.join(audio_dir, "frequencies")
    with open(output, 'wb') as freq_file:
        pickle.dump(decibel, freq_file)

def open_frequencies(video_file):
    audio_path = file_handler.get_dir_for_audio(video_file)
    audio_obj_path = os.path.join(audio_path, "frequencies")
    with open(audio_obj_path, 'rb') as freq_file:
        return pickle.load(freq_file)

def save_frames(output, frames):
    result = []
    for frame in frames:
        img = read_image_convert_to_grayscale(frame.fileName)
        result.append({"img": img, "sec": frame.sec, "count": frame.count})
    with open(output, 'wb') as frames_file:
        pickle.dump(result, frames_file)

def read_frames_audio(video_file):
    audio_path = file_handler.get_dir_for_audio(video_file)
    audio_obj_path = os.path.join(audio_path, "audio_obj")
    with open(audio_obj_path, 'rb') as frames_file:
        return pickle.load(frames_file)

def read_image_convert_to_grayscale(fileA):
	image_a = cv2.imread(fileA)
	image_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
	return image_a
