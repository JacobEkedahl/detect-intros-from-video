# ------------------------------------------------------------------------- #
# Compare two image files with different types of image sim algorithms      #
# The possible algorithms are: orb, mse, ssim and hash                 		#
# Ability to plot out images along with their similarity score				#
# For each algorithm the similarity score means different things			#
# ------------------------------------------------------------------------- #

import cv2
import imagehash
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from utils import constants as c


## list of hashes, preferably sorted
def find_all_matches_hash(hashes_A, hashes_B, threshold):
	result = []
	for hash_A in hashes_A:
		for hash_B in hashes_B:
			diff = hash_A["hash"] - hash_B["hash"]
			if diff < threshold:
				result.append({"count": hash_A["count"], "sec": hash_A["sec"]})
				break
	return result

## list of hashes, preferably sorted
def find_all_matches_hash_intro(hashes_A, hashes_B, intro_B, threshold):
	result = []
	matched_B = []
	for hash_A in hashes_A:
		for hash_B in hashes_B:
			diff = hash_A["hash"] - hash_B["hash"]
			if diff < threshold and hash_B["sec"] >= intro_B["start"] and hash_B["sec"] <= intro_B["end"] and hash_B not in matched_B:
				matched_B.append(hash_B)
				print("intro start: " + str(intro_B["start"]) + " - " + str(intro_B["end"]) + " - " + str(hash_A["sec"]))
				result.append({"count": hash_A["count"], "sec": hash_A["sec"]})
				break
	return result


def read_images(fileA, fileB):
	return cv2.imread(fileA), cv2.imread(fileB)

def read_images_convert_to_grayscale(fileA, fileB):
	image_a, image_b = read_images(fileA, fileB)
	image_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
	image_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)
	return (image_a, image_b)

def compare_images_mse(imageA, imageB):
	img_a, img_b = read_images_convert_to_grayscale(imageA, imageB)
	err = np.sum((img_a.astype("float") - img_b.astype("float")) ** 2)
	err /= float(img_a.shape[0] * img_b.shape[1])
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def compare_images_orb(fileA, fileB):
	try:
		img_a, img_b = read_images(fileA, fileB)
		orb = cv2.ORB_create()
		kp_a, desc_a = orb.detectAndCompute(img_a, None)
		kp_b, desc_b = orb.detectAndCompute(img_b, None)
		bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
		matches = bf.match(desc_a, desc_b)
		similar_regions = [i for i in matches if i.distance < 70]
		if len(matches) == 0:
			return 0
		return len(similar_regions) / len(matches)
	except cv2.error as e:
		print("could not compare, cv2 error")
		return 0

def compare_images_hash(imageA, imageB):
	hash0 = imagehash.average_hash(Image.open(imageA)) 
	hash1 = imagehash.average_hash(Image.open(imageB)) 
	print(str(hash0) + " - " + str(hash1))
	return hash0 - hash1

def compare_images_ssim(imageA, imageB):
	img_a, img_b = read_images_convert_to_grayscale(imageA, imageB)
	return ssim(img_a, img_b)

def plot_comparison(imageA, imageB, title, similarity):
	# setup the figure
	fig = plt.figure(title)
	plt.suptitle(title + " %.2f" % (similarity))

	# show first image
	ax = fig.add_subplot(1, 2, 1)
	plt.imshow(imageA, cmap = plt.cm.gray)
	plt.axis("off")

	# show the second image
	ax = fig.add_subplot(1, 2, 2)
	plt.imshow(imageB, cmap = plt.cm.gray)
	plt.axis("off")

	# show the images
	plt.show()
