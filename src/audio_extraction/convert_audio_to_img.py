import os
import subprocess

import imageio_ffmpeg as ffmpeg

import utils.constants as c


def convert_audio_to_spec(audio_file):
    audio_file = str(audio_file)
    pre, ext = os.path.splitext(audio_file)
    file_name = os.path.basename(audio_file)
    dir_name = os.path.dirname(audio_file)
    parts = file_name.replace('.wav', '').split('-')
    time = int(parts[1]) * c.AUDIO_SIZE_SPLITS
    output = os.path.join(dir_name, parts[1] + '-' + str(time) + '.jpg')
    command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", audio_file, "-lavfi", "showspectrumpic=s=100x100:mode=separate:legend=disabled:color=rainbow", "-y", output]
    subprocess.call(command, shell=True) 
