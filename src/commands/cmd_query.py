import db.video_repo as video_repo 
import utils.args_helper as args_helper

import annotations.dataset_annotation as dataset_annotation
from db.annotation_repo import Annotation
import db.annotation_repo as ann_repo

import utils.time_handler as time_handler


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

    # supports old method by first inserting all intros that have yet been inserted into ann_repo
    intros = dataset_annotation.get_dataset("intro")
    for intro in intros:
        ann_repo.insert(Annotation(intro['url'], "intro", intro['start'], intro['end']))
        

    shows = ann_repo.get_shows()
    i = 0
    print("\n\nFirst batch")
    while i < len(shows)*70/100:
        print(shows[i])
        i = i + 1
    print("\n\nSecond batch")
    while i < len(shows):
        print(shows[i])
        i = i + 1

    #for show in ann_repo.get_shows():
       # print(show)
      #  for season in ann_repo.get_show_seasons(show):
       ##     print(season)
       #     for intro in ann_repo.find_by_tag_show_season("intro", show, season):
      #         print(intro)

            






    
    

def execute_command(argv):   
    if args_helper.is_key_present(argv, "-videos"):
        __query_videos(argv)
    if args_helper.is_key_present(argv, "-stats"):
        __query_dataset(argv)
    else: 
        print("Error: invalid query.")    





