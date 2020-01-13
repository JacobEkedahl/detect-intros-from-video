import json
import db.video_repo as video_repo
import utils.time_handler as time_handler
import logging 


def export_dataset(path):
    logging.info("exported to %s " % path)
    output = { "intro": [], "pre-intro": [], "previous": []}
    for video in video_repo.find_all_with_intro_annotation():
        intro = video[video_repo.INTRO_ANNOTATION_KEY]
        if intro is not None: 
            entity = {
                "start": time_handler.seconds_to_str(intro['start']),
                "end": time_handler.seconds_to_str(intro['end']),
                "url": video['url']
            }
            output["intro"].append(entity)
        else: 
            logging.error("Intro was none: %s" % intro)
    with open(path, 'w') as outfile:
        json.dump(output, outfile, indent=4, sort_keys=True)


def import_dataset(path):
    logging.info("imported from %s " % path)
    with open(path) as json_file:
        data = json.load(json_file)
        for element in data["intro"]:
            start = element["start"]
            end = element["end"]
            if isinstance(start, str):
                start = time_handler.to_seconds(start)
            if isinstance(end, str):
                end = time_handler.to_seconds(end)
            video_repo.set_intro_annotation(element["url"], start, end)
            