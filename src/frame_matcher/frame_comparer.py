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


## list of frames, preferably sorted
def find_all_matches_hash(frames_A, frames_B, threshold):
	hashes_A = {}
	hashes_B = {}
	result = []
	for frame_A in frames_A:
		if frame_A.count not in hashes_A:
			hash_A = imagehash.average_hash(Image.open(frame_A.fileName))
			hashes_A[frame_A.count] = hash_A

		for frame_B in frames_B:
			if frame_B.count not in hashes_B:
				hash_B = imagehash.average_hash(Image.open(frame_B.fileName))
				hashes_B[frame_B.count] = hash_B

			diff = hashes_A[frame_A.count] - hashes_B[frame_B.count]
			if diff < threshold:
				print("add: " + str(frame_A.sec) + " - " + str(diff))
				result.append({"count": frame_A.count, "sec": frame_A.sec})
				break
	return result


## list of frames, preferably sorted
def find_all_matches_ssim(frames_A, frames_B, threshold):
	images_A = {}
	images_B = {}
	result = []
	for frame_A in frames_A:
		print(str(frame_A.count))
		if frame_A.count not in images_A:
			img_a = read_image_convert_to_grayscale(frame_A.fileName)
			images_A[frame_A.count] = img_a
		for frame_B in frames_B:
			if frame_B.count not in images_B:
				img_b = read_image_convert_to_grayscale(frame_B.fileName)
				images_B[frame_B.count] = img_b

			diff = ssim(images_A[frame_A.count], images_B[frame_B.count])
			#print(diff)
			if diff > 0.4:
				#print("add: " + str(frame_A.sec) + " - " + str(diff))
				result.append({"count": frame_A.count, "sec": frame_A.sec})
				break
	return result

def read_images(fileA, fileB):
	return cv2.imread(fileA), cv2.imread(fileB)

def read_images_convert_to_grayscale(fileA, fileB):
	image_a, image_b = read_images(fileA, fileB)
	image_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
	image_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)
	return (image_a, image_b)

def read_image_convert_to_grayscale(fileA):
	image_a = cv2.imread(fileA)
	image_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
	return image_a

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
