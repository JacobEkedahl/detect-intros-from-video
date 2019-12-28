# detect-intros-from-video

## To start
- git clone https://github.com/JacobEkedahl/detect-intros-from-video
- cd detect-intros-from-video
- pip install -r requirements.txt

## Build a dataset
- python src/main.py --build <fromStep> <toStep>
- fromStep, toStep = ["--start", "--frames", "--sim", "--seg", "--end"]
- example: python src/main.py --build --start --end 

## Train a hidden markov model and print predictions
- python src/hmm.py

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

## Find matching frames
- py src/main.py --match --files "video_file_path_A" "video_file_path_B"
- py src/main.py --match --files "video_file_path_A" "video_file_path_B"

## Compare similarities between two images (default algorithm is using the hash of images)
- py src/main.py --images "image_file_path_A" "image_file_path_B" --ssim<optinal> --print<optional>
- Types of similarity algorithms - (--orb, --ssim, --mse, --hash)
                                                                                                                    
## Extra
- Requires python of maximum version 3.7
- Run command from root folder (same directory as lib, src exists)
- All video files will be stored inside temp/videos
- Different types of constants values such as thresholds or paths for videos are defined in constants.py