import os
from pathlib import Path

TEMPFOLDERNAME = "temp"
VIDEOFOLDERNAME = "temp/videos"

def create_folderstructure_if_not_exists():
    if not os.path.exists(VIDEOFOLDERNAME):
        os.makedirs(VIDEOFOLDERNAME)

def get_full_path_videos():
    return os.path.join(str(os.getcwd()), VIDEOFOLDERNAME)

def get_full_path_temp():
    return os.path.join(str(os.getcwd()), TEMPFOLDERNAME)

def get_full_path_folder(folder_name):
    return os.path.join(get_full_path_temp(), folder_name)

def get_all_urls_from_file(file_name):
    text_file_path = os.path.join(get_full_path_temp(), file_name)
    return [line.rstrip('\n') for line in open(text_file_path)]

def get_all_mp4_files():
    files = []
    for filename in Path(get_full_path_videos()).rglob('*.mp4'):
        print(filename)
        files.append(filename)
        
    return files
