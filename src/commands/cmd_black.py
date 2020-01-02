"""
    Commands:

    * --black -stats -t 1.0
        Loops through all annotated data creating statistics with a margin of error of 1.0

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

ACCEPTED_ERR = 2.0

def __detect_black_sequences_for_all(forced):
    count = 0
    files = file_handler.get_all_mp4_files()
    if forced: 
        for file in files: 
            count = count + 1
            black.detect_blackness(file)
    else:
        for file in files: 
            if not black.file_has_been_detected(file): 
                count = count + 1
                black.detect_blackness(file)
    print("Blackdetection was used on %d/%d files." % (count, len(files)))


def __stats_intro_correlation(errMargin):
    blackIntroStartCount = 0
    blackIntroEndCount = 0
    processedIntrosCount = 0
    blackFrameIntroStart = 0
    blackFrameIntroEnd = 0
    blackFramePresentCount = 0

    startBlackCombinedCount = 0
    endBlackCombinedCount = 0
    totalBlackCombinedCount = 0 
    annotations = ann_repo.find_by_tag("intro")
    for ann in annotations:
        video = video_repo.find_by_url(ann['url'])
        introStart = time_handler.to_seconds(ann['start'])
        introEnd =time_handler.to_seconds(ann['end'])
        startHasBlackness = False 
        endHasBlackness = False 
        if black.FRAMES_KEY in video:
            blackFramePresentCount = blackFramePresentCount + 1
            for frame in video[black.FRAMES_KEY]:
                if abs(time_handler.to_seconds(frame['time']) - introStart) < errMargin:
                    blackFrameIntroStart = blackFrameIntroStart + 1
                    startHasBlackness = True 
                if abs(time_handler.to_seconds(frame['time']) - introEnd) < errMargin:
                    blackFrameIntroEnd = blackFrameIntroEnd + 1
                    endHasBlackness = True 

        if black.SEQUENCES_KEY in video: 
            processedIntrosCount = processedIntrosCount + 1
            print()
            print("%s s%02de%02d %f-%f" % (video['show'], video['season'], video['episode'], introStart, introEnd) )
            for seq in video[black.SEQUENCES_KEY]:
                if seq['start'] <= introStart + errMargin and introStart - errMargin <= seq['end']: 
                    blackIntroStartCount = blackIntroStartCount + 1
                    startHasBlackness = True 
                elif seq['end'] <= introEnd + errMargin and introEnd - errMargin <= seq['end']: 
                    blackIntroEndCount = blackIntroEndCount + 1 
                    endHasBlackness = True 
                print(seq)
        if startHasBlackness: 
            startBlackCombinedCount = startBlackCombinedCount + 1
        if endHasBlackness:
            endBlackCombinedCount = endBlackCombinedCount + 1
        if black.SEQUENCES_KEY in video or black.FRAMES_KEY in video:
            totalBlackCombinedCount = totalBlackCombinedCount + 1 

    print("\nmargin of error: %f " % errMargin)
    print("\nBlack sequences:")
    print("Intro start: %f%% of %d " % (blackIntroStartCount/processedIntrosCount*100, processedIntrosCount))
    print("Intro end: %f%% of %d" % (blackIntroEndCount/processedIntrosCount*100, processedIntrosCount))
    print("has black sequences: %d/%d" % (processedIntrosCount,len(annotations)))
    print("\nblack frames")
    print("Intro start: %f%% of %d " % (blackFrameIntroStart/blackFramePresentCount*100, blackFramePresentCount))
    print("Intro end: %f%% of %d" % (blackFrameIntroEnd/blackFramePresentCount*100, blackFramePresentCount))
    print("has black frames: %d/%d" % (blackFramePresentCount,len(annotations)))
    print("\nCombined")
    print("Intro start: %f%% of %d " % (startBlackCombinedCount/totalBlackCombinedCount*100, totalBlackCombinedCount))
    print("Intro end: %f%% of %d" % (endBlackCombinedCount/totalBlackCombinedCount*100, totalBlackCombinedCount))
    print("has any blackness: %d/%d" % (totalBlackCombinedCount,len(annotations)))

def execute(argv):
    if args_helper.is_key_present(argv, "-all"):
        if args_helper.is_key_present(argv, "-force"):
            __detect_black_sequences_for_all(True)
        else: 
            __detect_black_sequences_for_all(False)
        return
    if args_helper.is_key_present(argv, "-stats"):
        errMargin = args_helper.get_value_after_key(argv, "-threshold", "-t")
        if errMargin != "":
            __stats_intro_correlation(float(errMargin))
        else: 
            __stats_intro_correlation(ACCEPTED_ERR)

    file = args_helper.get_value_after_key(argv, "-input", "-i")
    if file != "" and ".mp4" in file: 
        black.detect_blackness(file)
        return 
