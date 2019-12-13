import sys as s

import utils.file_handler as file_handler
from downloader import svtplaywrapper

if __name__ == "__main__":
    file_handler.create_folderstructure_if_not_exists()
    if (len(s.argv) -1 < 1):
        print("need more arguments! (--dlv --file nameOfTxtFile numberOfEpisodes)")
        exit()

    if (s.argv[1] == "--dlv"):
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

    print("no valid arguments found")
