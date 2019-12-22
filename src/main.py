import pprint
import sys as s

import pipeline
import utils.file_handler as file_handler
from annotations import (annotate_subtitles, annotation_summary,
                         scene_annotation)
from downloader import svtplaywrapper
from frame_matcher import frame_cleaner as cleaner
from frame_matcher import frame_comparer as comparer
from frame_matcher import video_matcher as v_matcher
from frame_matcher import video_to_audio_frames as v_a
from frame_matcher import video_to_frames as vf
from segmenter import scenedetector

if __name__ == "__main__":
    file_handler.create_folderstructure_if_not_exists()
    if (len(s.argv) - 1 < 1):
        print("need more arguments! (--dlv --file nameOfTxtFile numberOfEpisodes)")
        exit()
    if (s.argv[1] == "--audio"):
        v_a.get_audio_from_video()
    elif (s.argv[1] == "--build"):
        pipeline.build_dataset_from_step(s.argv[2], s.argv[3])
    elif (s.argv[1] == "--rframes"):
        file_one = s.argv[2]
        cleaner.remove_similar_frames(file_one)
        exit()
    elif (s.argv[1] == "--frames"):
        mp4_files = file_handler.get_all_mp4_files()
        for mp4_file in mp4_files:
            vf.video_to_frames_check(str(mp4_file))
        exit()
    elif (s.argv[1] == "--match"):
        if len(s.argv) > 2:
            if s.argv[2] == "--files":
                file_one = s.argv[3]
                file_two = s.argv[4]
                v_matcher.find_all_matches_hash(file_one, file_two)
                exit()
            elif s.argv[2] == "--file":
                file_one = s.argv[3]
                v_matcher.find_all_matches(file_one)
                exit()
    elif (s.argv[1] == "--compare"):
        if len(s.argv) > 2:
            if s.argv[2] == "--images":
                file_one = s.argv[3]
                file_two = s.argv[4]
                result = 0
                title = "Comparison"
                if "--orb" in s.argv:
                    result = comparer.compare_images_orb(file_one, file_two)
                    title = "Orb similarity"
                elif "--ssim" in s.argv:
                    result = comparer.compare_images_ssim(file_one, file_two)
                    title = "SSIM similarity"
                elif "--mse" in s.argv:
                    result = comparer.compare_images_mse(file_one, file_two)
                    title = "MSE similarity"
                elif "--hash" in s.argv:
                    result = comparer.compare_images_hash(file_one, file_two)
                    title = "HASH similarity"
                else:
                    result = comparer.compare_images_orb(file_one, file_two)
                    title = "Orb similarity"
                if "--plot" in s.argv:
                    img_a, img_b = comparer.read_images(file_one, file_two)
                    comparer.plot_comparison(img_a, img_b, title, result)
                print("similarity result: " + str(result))
 
    elif (s.argv[1] == "--dlv"):
        noOfArgs = len(s.argv) - 1
        if (noOfArgs < 2):
            print("need more arguments!")
            exit()
        if (s.argv[2] == "--file"):
            name_textfile = s.argv[3]
            number_of_episodes = s.argv[5]
            svtplaywrapper.start(name_textfile, number_of_episodes)
        elif (s.argv[2] == "--url"):
            url_path = s.argv[3]
            svtplaywrapper.download_video(url_path)
            
        print("finnished downloading!")
        exit()

    elif (s.argv[1] == "--seg"):
        if (len(s.argv) -1 < 2):
            scenedetector.segment_all_videos()
        elif s.argv[2].endswith(".mp4"):
            video_file = s.argv[2]
            scenedetector.segment_video(video_file)

    elif (s.argv[1] == "--ann"):
        if (s.argv[2] == "--result"):
            annotation_summary.execute(s.argv)
        else:
            scene_annotation.execute(s.argv)
        exit()
    elif (s.argv[1] == "--subs"):
        annotate_subtitles.execute(s.argv)
        exit()

    else:
        print("no valid arguments found")
