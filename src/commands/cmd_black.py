"""
    Commands:

    * --black -stats     
        Loops through all annotated data creating statistics

    * --black -i temp/videos/video.mp4 
        Detects all black sequences and frames for input video. 

    * --black -all
        Detects all black sequences and frames in videos under temp/. Will skip previously detected.

    * --black -all -force
        Detects all black sequences and frames in videos under temp/. Will not skip previously detected.
"""

import segmenter.blackdetector as black 
import utils.args_helper as args_helper
import utils.time_handler as time_handler
import utils.file_handler as file_handler
import db.annotation_repo as ann_repo
import db.video_repo as video_repo 

ACCEPTED_ERR = 4.0

def __detect_black_sequences_for_all(forced):
    count = 0
    files = file_handler.get_all_mp4_files()
    if forced: 
        for file in files: 
            count = count + 1
            black.detect_black_sequences(file)
    else:
        for file in files: 
            if not black.file_has_been_detected(file): 
                count = count + 1
                black.detect_black_sequences(file)
    print("Blackdetection was used on %d/%d files." % (count, len(files)))


def __stats_intro_correlation():
    blackIntroStartCount = 0
    blackIntroEndCount = 0
    processedIntrosCount = 0
    annotations = ann_repo.find_by_tag("intro")
    for ann in annotations:
        video = video_repo.find_by_url(ann['url'])
        introStart = time_handler.to_seconds(ann['start'])
        introEnd =time_handler.to_seconds(ann['end'])
        if 'blackSequences' in video: 
            processedIntrosCount = processedIntrosCount + 1
            print()
            print("%s s%02de%02d %f-%f" % (video['show'], video['season'], video['episode'], introStart, introEnd) )
            for seq in video['blackSequences']:
                if seq['start'] <= introStart + ACCEPTED_ERR and introStart - ACCEPTED_ERR <= seq['end']: 
                    blackIntroStartCount = blackIntroStartCount + 1
                elif seq['end'] <= introEnd + ACCEPTED_ERR and introEnd - ACCEPTED_ERR <= seq['end']: 
                    blackIntroEndCount = blackIntroEndCount + 1 
                print(seq)
    print()
    print("Intro start: %f%% of %d " % (blackIntroStartCount/processedIntrosCount*100, processedIntrosCount))
    print("Intro end: %f%% of %d" % (blackIntroEndCount/processedIntrosCount*100, processedIntrosCount))
    print("has black sequences: %d/%d" % (processedIntrosCount,len(annotations)))


def execute(argv):
    if args_helper.is_key_present(argv, "-all"):
        if args_helper.is_key_present(argv, "-force"):
            __detect_black_sequences_for_all(True)
        else: 
            __detect_black_sequences_for_all(False)
        return
    if args_helper.is_key_present(argv, "-stats"):
        __stats_intro_correlation()

    file = args_helper.get_value_after_key(argv, "-input", "-i")
    if file != "" and ".mp4" in file: 
        black.detect_black_sequences(file)
        return 
