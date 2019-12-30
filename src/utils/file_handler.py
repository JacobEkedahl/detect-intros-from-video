import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from . import constants as c

TEMPFOLDERNAME = "temp"
VIDEOFOLDERNAME = "videos"
URLSTEXTFILENAME = "video-serier.txt"
DATAFOLDERNAME = "data"
ANNOTATIONS = "dataset.json"

def create_folderstructure_if_not_exists():
    if not os.path.exists(get_full_path_videos()):
        os.makedirs(get_full_path_videos())

def get_video_file_from_seg(seg_file):
    return str(seg_file).replace('.json', '.mp4')

def get_all_other_videos_in_series(video_file):
    parent_dir = os.path.dirname(video_file)
    other_videos = get_all_files_by_type(parent_dir, 'mp4')
    #print(other_videos)
    this_video_index = other_videos.index(video_file)
    other_videos.remove(str(video_file))

    season = get_season_from_video_file(video_file)
    series = get_series_from_video_file(video_file)
    result = []
    videos_to_remove = []
    two_back = this_video_index - 3
    if two_back < 0:
        two_back = 0
    for i in range(two_back, len(other_videos)):
        video = other_videos[i]
        if len(result) >= 6:
            break
        if get_season_from_video_file(video_file) == season and series in video_file:
            result.append(video)
            videos_to_remove.append(video)
    for video in videos_to_remove:
        other_videos.remove(str(video))

    if len(result) < 6:
        how_much_to_extend = 6 - len(result)
        if how_much_to_extend > len(other_videos):
            result.extend(other_videos[:len(other_videos)])
        else:
            result.extend(other_videos[:how_much_to_extend])
    return result

def get_other_videos_in_series(video_file):
    parent_dir = os.path.dirname(video_file)
    other_videos = get_all_files_by_type(parent_dir, 'mp4')
    other_videos.remove(str(video_file))
    return other_videos

def get_intros_from_videos(video_files):
    intros = get_intros()
    result = []
    for video_file in video_files:
        seg_file = get_seg_file_from_video(video_file)
        with open(seg_file) as json_file:
            data = json.load(json_file)
            url = data['url']
            for intro in intros:
                if intro['url'] == url:
                    result.append(intro)
                    break
    if len(result) == 0:
        return None
    return result

def get_season_from_video_file(video_file):
    file_name = os.path.basename(video_file)
    season_episode = file_name.split('.')[1]
    return season_episode[1:3]
    
def get_series_from_video_file(video_file):
    file_name = os.path.basename(video_file)
    return file_name.split('.')[0]

def get_intros():
    intro_file = get_full_path_intros()
    with open(intro_file) as json_file:
        data = json.load(json_file)
        return data['intro']

def get_url_from_file_name(video_file):
    segFile = get_seg_file_from_video(video_file)
    with open(segFile) as json_file:
        try:
            data = json.load(json_file)
        except:
            print(str(segFile))
            exit()
        return data['url']
    return None

def get_file_name_from_url(url):
    seg_files = get_all_files_by_type(get_full_path_videos(), 'json')
    for segmentationFile in seg_files:
        with open(segmentationFile) as json_file:
            data = json.load(json_file)
            if data['url'] == url:
                return str(segmentationFile).replace('.json', '-.mp4')
    return None

def get_all_urls_from_file(file_name):
    text_file_path = os.path.join(get_full_path_temp(), file_name)
    urls = [line.rstrip('\n') for line in open(text_file_path)]
    return [item for item in urls if item.startswith("http")]

def get_seg_file_from_video(video_file):
    return str(video_file).replace('.mp4', '.json')

def get_srt_from_video(video_file):
    return str(video_file).replace('-converted.mp4', '.srt')

def get_all_files_by_type(path, fileType):
    files = []
    for filename in Path(path).rglob('*.' + fileType):
        files.append(str(filename))
    return files

def get_all_mp4_files():
    return get_all_files_by_type(get_full_path_videos(), 'mp4')

def get_all_mp4_files_not_matched():
    all_videos = get_all_mp4_files()
    result = []
    for video_file in all_videos:
        seg_file = get_seg_file_from_video(video_file)
        with open(seg_file) as json_file:
            data = json.load(json_file)
            if c.DESCRIPTION_MATCHES not in data['scenes'][0]:
                result.append(video_file)
             #   print(video_file)
    return result

def get_all_unmerged_files():
    files = []
    types = ["*.audio.ts", "*.m4a"] #find audio files and match with videofiles

    for ext in types:
        audioExtNoStar = ext[1:]
        for audioName in Path(get_full_path_videos()).rglob(ext):
            audioName = str(audioName)
          #  print("audioname: " + audioName)
            videoName = audioName.replace(audioExtNoStar, audioVideoTranslator[audioExtNoStar], 1)
            fileName = audioName.replace(audioExtNoStar,  '', 1)
            files.append(FileInfo(fileName, audioName, videoName ))
    return files

def does_meta_contain_obj(obj_type, video_file):
    dir = get_dir_for_meta(video_file)
    return os.path.isfile(os.path.join(dir, obj_type))

# Helper functions
def get_full_path_folder(folder_name):
    return os.path.join(get_full_path_temp(), folder_name)

def get_all_urls_from_temp():
    return get_all_urls_from_file(URLSTEXTFILENAME)

def get_full_path_temp():
    return os.path.join(str(os.getcwd()), TEMPFOLDERNAME)
    
def get_full_path_data():
    return os.path.join(str(os.getcwd()), DATAFOLDERNAME)

def get_full_path_intros():
    return os.path.join(str(get_full_path_data()), ANNOTATIONS)

def get_full_path_videos():
    return os.path.join(get_full_path_temp(), VIDEOFOLDERNAME)

def get_dir_for_meta(video_file):
    return get_dir_by_type(video_file, "-meta")

def get_dir_by_type(video_file, ext_type):
    dir_name = str(video_file).replace('-converted.mp4', ext_type)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

audioVideoTranslator = {".audio.ts": ".ts", ".m4a": ".mp4"}
class FileInfo:
    def __init__(self, fileName, audioName, videoName):
        self.fileName = fileName
        self.audioName = audioName
        self.videoName = videoName
