import utils.args_helper as args_helper
import segmenter.scenedetector as scenedetector

def __segment_all_scendetect(forced):
    scenedetector.segment_all_videos()


def __segment_scendetect(video_file):
    scenedetector.segment_video(video_file)

    
def execute(argv):
    if args_helper.is_key_present(argv, "-all"):
        if args_helper.is_key_present(argv, "-force"):
            __segment_all_scendetect(True)
        else: 
            __segment_all_scendetect(False)
        return
    file = args_helper.get_value_after_key(argv, "-input", "-i")
    if file != "" and ".mp4" in file: 
        __segment_scendetect(file)

