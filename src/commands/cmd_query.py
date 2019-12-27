import db.video_repo as video_repo 
import utils.args_helper as args_helper

import annotations.dataset_annotation as dataset_annotation


def __query_videos(argv):
    season = args_helper.get_value_after_key(argv, "-season", "-season")
    show = args_helper.get_value_after_key(argv, "-show", "-show")
    videos = []
    if show != "":
        if season != "":
            videos = video_repo.find_by_show_and_season(show, int(season))
        else:
            videos = video_repo.find_by_show(show)
    else:
        videos = video_repo.find_all()
    for v in videos: 
        if v['downloaded']:
            print("%s s%02de%02d %s %s" % (v['show'], v['season'], v['episode'], v['downloaded'], v['fullpath']))
        else:
            print("%s s%02de%02d %s " % (v['show'], v['season'], v['episode'], v['downloaded']))


def __query_dataset(argv):
    intros = dataset_annotation.get_dataset("intro")
    
    
    for intro in intros:
        video = video_repo.find_by_url(intro['url'])
        print(video['show'])


    
    

def execute_command(argv):   
    if args_helper.is_key_present(argv, "-videos"):
        __query_videos(argv)
    if args_helper.is_key_present(argv, "-stats"):
        __query_dataset(argv)
    else: 
        print("Error: invalid query.")    





