
import subprocess

import imageio_ffmpeg as ffmpeg


def extract(fileName):
    output = "gui/temp/" + fileName
    command = [ffmpeg._utils.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "panic", "-i", "gui/temp/current-converted.mp4", "-vn", "-acodec", "libvorbis", "-y", output]
    subprocess.call(command) 
