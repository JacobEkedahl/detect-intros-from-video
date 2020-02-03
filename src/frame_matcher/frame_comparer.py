# ------------------------------------------------------------------------- #
# Compare two h files with different types of image sim algorithms      #
# ------------------------------------------------------------------------- #

import cv2
import imagehash
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from utils import constants as c


def find_all_matches_hash_intro(hashes_A, hashes_B, intro_B, threshold):
	result = []
	result_intro = []

	for hash_A in hashes_A:
		for hash_B in hashes_B:
			diff = hash_A["hash"] - hash_B["hash"]
			if diff < threshold:
				result.append({"count": hash_A["count"], "sec": hash_A["sec"]})
				if intro_B is not None and hash_B["sec"] >= intro_B["start"] and hash_B["sec"] <= intro_B["end"]:
					result_intro.append({"count": hash_A["count"], "sec": hash_A["sec"]})
				break
	return (result, result_intro)
