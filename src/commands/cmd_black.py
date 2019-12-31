import re

import segmenter.blackdetector as black 
import utils.args_helper as args_helper

def execute(argv):
    file = args_helper.get_value_after_key(argv, "-input", "-i")
    if file != "" and ".mp4" in file: 
        black.detect_black_sequences(file)
        return 
