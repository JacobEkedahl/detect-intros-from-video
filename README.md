# detect-intros-from-video

## To start
- git clone https://github.com/JacobEkedahl/detect-intros-from-video
- cd detect-intros-from-video
- pip install -r requirements.txt

## Build a dataset
- python src/main.py --build <fromStep> <toStep>
- fromStep, toStep = ["--start", "--frames", "--sim", "--end"]
- example: python src/main.py --build --start --end 

## Run svtplaydownloader:
- python src/main.py --dlv --url "url"

## Run Scene Detector:
- python src/main.py --seg
- python src/main.py --seg temp/myvideo.mp4

## Run downloader and segmentor at once
- Move the file of all videos to download under temp/ in root called video-serier.txt
- python src/main.py --start

## Extract frames from video and save in folders
- python src/main.py --frames

## Clean frames connected to video (can be done after extracting frames)
- py src/main.py --rframes "video_file_path"

## Find matching frames
- py src/main.py --match --files "video_file_path_A" "video_file_path_B"
- py src/main.py --match --files "video_file_path_A" "video_file_path_B"

## Compare similarities between two images (default algorithm is using the hash of images)
- py src/main.py --images "image_file_path_A" "image_file_path_B" --ssim<optinal> --print<optional>
- Types of similarity algorithms - (--orb, --ssim, --mse, --hash)

## Annotator 

- Manual annotations 

Annotate a file with a intro, intro can be replaced with any word. Optional arguments -print and -force

    py src/main.py --ann al-pitcher-pa-paus.json -s 00:00:00 -e 00:00:15 -t intro                                                      
                                                    
Delete annotation of 'intro' from a file

    py src/main.py --ann al-pitcher-pa-paus.json -delete -t intro 

- Statistics

Prints the results of all files annotated with 'intro inside temp/. You can specify other directories by using -path followed by the directory.

    py src/main.py --result -tag 'intro'                    

Filters: 

    -filter lt 1                    // Only include errors that are less than 1.0 seconds
    -filter gt 1                    // Only include errors that are greater than 1.0 seconds
    -contains allt-jag-inte-mins    // Only includes files that contain the substring in their name
                                                                                                                        
## Extra
- Run command from root folder (same directory as lib, src exists)
- All video files will be stored inside temp/videos
- Different types of constants values such as thresholds or paths for videos are defined in constants.py