import sys as s

from downloader import svtplaywrapper
from segmenter import scenedetector


if __name__ == "__main__":
    if (len(s.argv) -1 < 1):
        print("need more arguments! (--dlv --file nameOfTxtFile nameOfFolder numberOfEpisodes)")
        exit()

    if (s.argv[1] == "--dlv"):
        noOfArgs = len(s.argv) - 1
        if (noOfArgs < 2):
            print("need more arguments!")
            exit()

        if (s.argv[2] == "--file"):
            name_textfile = s.argv[3]
            name_folder =  s.argv[4]
            number_of_episodes = s.argv[5]
            svtplaywrapper.start(name_textfile, name_folder, number_of_episodes)
        elif (s.argv[2] == "--url"):
            url_path = s.argv[3]
            name_folder = s.argv[4]
            svtplaywrapper.download_video(url_path, name_folder)
        print("finnished downloading!")
        exit()
    # C:\Users\tiago\Desktop\Exjobb\detect-intros-from-video\temp
    elif (s.argv[1] == "--seg"):
        scenedetector.execute(s.argv)
        exit()

    print("no valid arguments found")
