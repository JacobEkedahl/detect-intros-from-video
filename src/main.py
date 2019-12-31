import pprint
import sys as s
from commands import cmd_dataset, cmd_query, cmd_segment, cmd_videos

import downloader.scrapesvt as scrapesvt
import pipeline
import utils.file_handler as file_handler
from annotations import (annotate_subtitles, annotation_summary,
                         dataset_annotation, scene_annotation)
from audio_extraction import video_to_pitches as v_p
from classifier import prob_calculator
from downloader import svtplaywrapper
from frame_matcher import frame_comparer as comparer
from frame_matcher import video_matcher as v_matcher
from frame_matcher import video_to_hashes as vf
from segmenter import scenedetector
from utils import cleaner, extractor

if __name__ == "__main__":
    file_handler.create_folderstructure_if_not_exists()
    if (len(s.argv) - 1 < 1):
        print("need more arguments! (--dlv --file nameOfTxtFile numberOfEpisodes)")
        exit()
    elif (s.argv[1] == "--clean"):
        #if len(s.argv) >= 4:
        #    cleaner.remove_annotation_from_series(s.argv[2], s.argv[3])
       # else:
      #  cleaner.remove_annotations(s.argv[2])
        if len(s.argv) >= 4:
            cleaner.remove_annotation_from_series(s.argv[2], s.argv[3])
      #  else:
         #   cleaner.remove_annotations(s.argv[2])
    elif (s.argv[1] == "--train"):
        prob_calculator.fun_test()
    elif (s.argv[1] == "--testMatcher"):
        v_matcher.find_errors()
    elif (s.argv[1] == "--build"):
        pipeline.build_dataset_from_step(s.argv[2], s.argv[3])
    elif (s.argv[1] == "--frames"):
        mp4_files = file_handler.get_all_mp4_files()
        for mp4_file in mp4_files:
            vf.save_hashes(str(mp4_file))
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

    elif (s.argv[1] == "--scrape"):
        scrapesvt.execute(s.argv)
        exit()
    elif (s.argv[1] == "--videos"):
        cmd_videos.execute(s.argv)
        exit()

    elif (s.argv[1] == "--seg"):
        cmd_segment.execute(s.argv)
        exit()
    
    elif (s.argv[1] == "--dataset"):
        cmd_dataset.execute(s.argv)
        exit()

    elif (s.argv[1] == "--subs"):
        annotate_subtitles.execute(s.argv)
        exit()

    else:
        print("no valid arguments found")
