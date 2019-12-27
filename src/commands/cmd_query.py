import db.video_repo as video_repo 
import utils.args_helper as args_helper

def execute_command(argv):   

    if args_helper.is_key_present(argv, "-videos"):
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

    else: 
        print("Error: invalid query.")    




