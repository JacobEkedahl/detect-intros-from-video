import os
from pathlib import Path

TEMPFOLDERNAME = "temp"
VIDEOFOLDERNAME = "videos"
URLSTEXTFILENAME = "video-serier.txt"

def create_folderstructure_if_not_exists():
    ##scrape svt and fetch urls, save in temp
    if not os.path.exists(get_full_path_videos()):
        os.makedirs(get_full_path_videos())

def get_full_path_videos():
    return os.path.join(get_full_path_temp(), VIDEOFOLDERNAME)

def get_full_path_temp():
    return os.path.join(str(os.getcwd()), TEMPFOLDERNAME)

def get_full_path_folder(folder_name):
    return os.path.join(get_full_path_temp(), folder_name)

def get_all_urls_from_temp():
    return get_all_urls_from_file(URLSTEXTFILENAME)

def get_all_urls_from_file(file_name):
    text_file_path = os.path.join(get_full_path_temp(), file_name)
    urls = [line.rstrip('\n') for line in open(text_file_path)]
    return [item for item in urls if item.startswith("http")]

def get_all_mp4_files():
    files = []
    for filename in Path(get_full_path_videos()).rglob('*.mp4'):
        print(filename)
        files.append(filename)
        
    return files
