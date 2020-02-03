SEC_PER_FRAME = 0.3 # seconds
IMAGE_WIDTH = 256
IMAGE_HEIGHT = 256
HASH_CUTOFF = 5

SEQUENCE_THRESHOLD = 4 # seconds
MIN_LENGTH_SEQUENCE = 5 # seconds
FRACTION_SIZE_PREINTRO = 0.35 #35 percentage
PREINTRO_START = 30 # limit for a preintro to start in seconds
DOWNSCALE_FACTOR = 10

MARGIN_BETWEEN_PITCH = 1
MIN_SEQ_LENGTH = 10 #seconds
SEGMENT_LENGTH = 0.1 #seconds

NUMBER_OF_NEIGHBOR_VIDEOS = 6

HASH_NAME = "hashes"
DESCRIPTION_INTRO = "intro"
DESCRIPTION_MATCHES_INTRO = "matches_intro"
DESCRIPTION_MATCHES = "matches"

#HMM
TRAIN_SIZE = 0.7 # fraction of the training set size, rest is test
START_SEED = 0

# Processing  
TEMP_FOLDER_PATH = "temp"
VIDEO_FOLDER_PATH = "temp\\videos"
VIDEO_GENRES = ["serier"]
VIDEO_START_LEN = 480 
DELETE_VIDEO_AFTER_EXTRACTION = False # Must first perform video comparison before video files are removed...  
SAVE_TO_FILE = True 
SAVE_TO_DB = True 

SCHEDULED_PREPROCESSING_START = "01:00"
SCHEDULED_PREPROCESSING_END = "13:00"

TIMEOUT_DOWNLOAD = 900 #seconds
