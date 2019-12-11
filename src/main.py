import sys as s

from downloader import svtplaywrapper

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
            fileName = s.argv[3]
            nameOfFolder =  s.argv[4]
            numberOfEpisodes = s.argv[5]
            svtplaywrapper.start(fileName, nameOfFolder, numberOfEpisodes)
        elif (s.argv[2] == "--url"):
            urlpath = s.argv[3]
            nameOfFolder = s.argv[4]
            svtplaywrapper.downloadVideo(urlpath, nameOfFolder)

        print("finnished downloading!")
        exit()

    print("no valid arguments found")
