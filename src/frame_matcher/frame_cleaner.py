import os

import utils.constants as c
import utils.file_handler as file_handler

from . import frame_comparer as comparer


def remove_similar_frames(video_file):
    frames = file_handler.get_framespaths_from_video(video_file)
    frames.sort(key=lambda x: x.count, reverse=False)
    files_to_remove = []

    for i in range(len(frames) -1):
        j = i + 1
        #ssim_val = comparer.compare_images_ssim(frames[i].fileName, frames[j].fileName)
        orb_val = comparer.compare_images_orb(frames[i].fileName, frames[j].fileName)
        print(str(orb_val) + " - "  + str(i) + " - " + str(j))

        if orb_val > c.THRESHOLD_ORB:
            files_to_remove.append(frames[j].fileName)
    remove_all_files(files_to_remove)

def remove_all_files(list_of_files):
    for file in list_of_files:
        os.remove(file)
