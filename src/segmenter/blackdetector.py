import imageio_ffmpeg as ffmpeg
import subprocess
import re
import os 
import json 

import db.video_repo as video_repo 

SEQ_KEY = 'blackSequences'
FRAMES_KEY = 'blackFrames'
PRINT_OUTPUT = False   
SAVE_TO_DB = True
SAVE_TO_FILE = True 

def detect_black_sequences(video_file):
    cmd = ( "%s -i temp/invis.mp4 -vf blackdetect=d=0.1:pix_th=0.10 -an -f null -y /dev/null" % ffmpeg._utils.get_ffmpeg_exe() ).split(" ")
    output = subprocess.Popen( cmd, stderr=subprocess.PIPE ).communicate()[1]
    blackFrames = []
    blackSequences = []
    for line in output.decode('utf-8').splitlines():
        if "blackdetect" in line:
            # Line = [blackdetect @ 03e7e280] black_start:0 black_end:4.24 black_duration:4.24
            data = re.findall(r"[-+]?\d*\.?\d+|\d+", line.split("]")[1]) 
            blackSequences.append({ 
                'start': float(data[0]),
                'end': float(data[1]),
                'duration': float(data[2])
            })
        elif "frame=" in line: 
            # frame=12001 fps=420 q=-0.0 Lsize=N/A time=00:08:00.04 bitrate=N/A speed=16.8x
            print("L: %s" % line)
            time = line.split("time=")[1].split(" bitrate=")[0]
            frame = line.split("frame=")[1].split(" fps=")[0]
            blackFrames.append({
                'frame': int(frame),
                'time': time
            })   
        
    if SAVE_TO_FILE: 
        json_path = video_file.replace('.mp4', '') + '.json'
        data = {}
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                data = json.load(json_file)

        data[SEQ_KEY] = blackSequences
        data[FRAMES_KEY] = blackFrames
        with open(json_path, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)
    
    if SAVE_TO_DB: 
        try: 
            video_repo.set_data_by_file(os.path.basename(video_file), SEQ_KEY, blackSequences)
            video_repo.set_data_by_file(os.path.basename(video_file), SEQ_KEY, blackFrames)
        except: 
            print("Warning: did not save scenes to db.")

    if PRINT_OUTPUT: 
        for seq in blackSequences: 
            print(seq)
        for f in blackFrames: 
            print(f)

    print("Darkness extraction of %s completed. " % video_file)
    
    return blackSequences, blackFrames
   