import imageio_ffmpeg as ffmpeg
import subprocess
from subprocess import STDOUT, check_output
from pathlib import Path

# if the timeout is exceeded the file is not considered corrupt
TIMEOUT_TIME_IN_SECONDS = 1 

# Returns true if the mp4 file is corrupted
def file_has_corruption(mp4_file):
    cmd = [ffmpeg._utils.get_ffmpeg_exe(), "-v", "error", "-i", mp4_file, "-f", "null", "-"]
    try:
        check_output(cmd, stderr=STDOUT, timeout=TIMEOUT_TIME_IN_SECONDS)
    except subprocess.CalledProcessError:                                                                                                   
        return True
    except subprocess.TimeoutExpired:
        return False
    return False 

# Notice that the execution of this can take up to  [timeout] * [number of mp4 files], uncurrpted files typically hit the timeout
def find_all_corrupted_mp4_files():
    corrupted = []
    for mp4 in Path("temp").rglob('*.mp4'):
        if file_has_corruption(mp4):
            corrupted.append(mp4)
    return corrupted
