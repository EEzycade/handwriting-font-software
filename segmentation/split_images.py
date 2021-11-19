import argparse
import random
from tqdm import tqdm

import numpy as np
from PIL import Image

from sklearn.cluster import SpectralClustering
from sklearn.neighbors import KNeighborsClassifier

def mask_image(mask, original):
	mask = np.asarray(Image.fromarray(mask).resize(original.size, Image.NEAREST))
	img = np.where(mask, np.asarray(original)[:,:,0], 255).astype(np.uint8)
	
	x, y = np.where(mask)
	x_min, x_max = x.min(), x.max()
	y_min, y_max = y.min(), y.max()
	img = img[x_min:x_max, :]
	img = img[:, y_min:y_max]
	return img

def clustered_image(colors, clusters, black_pixels, sample=np.zeros((0,2), dtype=int)):
	buffer = colors[clusters].reshape((black_pixels.shape[0], black_pixels.shape[1], 3))
	buffer[black_pixels] = (0, 0, 0)
	buffer[sample[:,0], sample[:,1]] = (255, 0, 0)
	return Image.fromarray(buffer)


def __main__(args):
	original = Image.open(args.image)
	img = original.resize((original.size[0]//args.downsample, original.size[1]//args.downsample))
	
	black_pixels = np.asarray(img).mean(axis=2) < 128
	black_pixel_locations = np.array(np.where(black_pixels)).T
	
	sample = np.array(random.sample(list(black_pixel_locations), args.sample_size))
	clusterer = SpectralClustering(args.characters, gamma=args.gamma)
	knn = KNeighborsClassifier(5)
	
	knn.fit(sample, clusterer.fit_predict(sample))

	coordinates = np.indices(img.size).transpose((2, 1, 0)).reshape(-1, 2)[:,::-1]
	clusters = knn.predict(coordinates)

	if args.show_clustering:
		colors = np.random.randint(0, 255, (args.characters,3), dtype=np.uint8)
# 		clustered_image(colors, clusters, black_pixels, sample=sample).save(args.output + "/clusters.png")
		clustered_image(colors, clusters, black_pixels).save(args.output + "/clusters.png")
	
	clusters = clusters.reshape((img.size[1], img.size[0]))
	for k in tqdm(range(args.characters)):
		img = mask_image(clusters == k, original)
		img = Image.fromarray(img)
		if args.rename:
			color = np.full((args.characters,3), 255, dtype=np.uint8)
			color[k, 1:] = 0
			img_in_cluster = clustered_image(color, clusters.flatten(), black_pixels)
			try: display(img_in_cluster)
			except NameError: img_in_cluster.show()
			letter = input()
		else:
			letter = f"image-{k}"
		img.save(f"{args.output}/{letter}.png")
		


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--image", type=str, required=True)
	parser.add_argument("--sample-size", default=3000, type=int)
	parser.add_argument("--gamma", default=0.01, type=float)
	parser.add_argument("--characters", default=52, type=int)
	parser.add_argument("--output", type=str, required=True)
	parser.add_argument("--show-clustering", type=bool, default=False)
	parser.add_argument("--downsample", type=int, default=10)
	parser.add_argument("--rename", type=bool, default=False)
	args = parser.parse_args()
	__main__(args)
