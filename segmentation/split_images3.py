# requires: pip install opencv-contrib-python
import argparse
from tqdm import tqdm
from uuid import uuid4
from PIL import Image, ImageDraw
import cv2
import numpy as np

def segment(x, thresh=1):
    cluster_segments = []
    start = -2
    stop = -2
    for x in x:
        if stop + 1 == x:
            stop = x
        else:
            if stop - start > thresh:
                cluster_segments.append((start + stop) // 2)
            start = stop = x
    if stop - start > thresh:
        cluster_segments.append((start + stop) // 2)
    return cluster_segments

def draw_boxes(img, boxes):
    img = img.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    for box in boxes:
        draw.rectangle(box, outline=(255, 0, 0), width=5)
    return img

def split_rows(img, blur_factor=150, min_area=200, pad_width=5, pad_height=5):
	blurred = Image.fromarray(cv2.blur((255*np.asarray(img)).astype(np.uint8), (blur_factor, 1)) == 255)
	_, clusters, stats, _ = cv2.connectedComponentsWithStats(
		(255*~np.asarray(blurred)).astype(np.uint8)
	)

	row_masks = []
	row_boxes = []
	for i in range(1, stats.shape[0]):
		x1, y1, w, h, area = stats[i, :]
		if area >= min_area:
			x2, y2 = x1 + w, y1 + h
			x1, y1 = max(x1 - pad_width, 0),           max(y1 - pad_height, 0)
			x2, y2 = min(x2 + pad_width, img.size[0]), min(y2 + pad_height, img.size[1])

			row_masks.append(clusters == i)
			row_boxes.append((x1, y1, x2, y2))
	return row_masks, row_boxes

def split_cols(img, max_pixels=0):
	filled_cols ,= np.where((np.asarray(img) == 0).sum(axis=0) <= max_pixels)
	splits = segment(filled_cols, thresh=1)
	return list(zip(splits[:-1], splits[1:]))

def crop_and_mask(img, box, mask):
	return Image.fromarray(
		np.where(mask[:,:,None], np.asarray(img), 255).astype(np.uint8)
	).crop(box)

def crop_around_box(img, box, pad_width=100, pad_height=100):
	return img.crop((
		max(box[0] - pad_width, 0),
		max(box[1] - pad_height, 0),
		min(box[2] + pad_width, img.size[0]),
		min(box[3] + pad_height, img.size[1])
	))

def display_image(img):
	try:
		# if in IPython
		from IPython.display import clear_output
		clear_output()
		display(img)
	except NameError:
		img.show()

def __main__(args):
	original = Image.open(args.image).convert("RGB")
	img = Image.fromarray((np.asarray(original) > 192).all(axis=2))
	
	thin = Image.fromarray(
		255-cv2.ximgproc.thinning(
			(255*(~np.asarray(img))).astype(np.uint8)
		)
	)
	
	row_masks, row_boxes = split_rows(img)
	
	masks, boxes = [], []
	for mask, (_, y1, _, y2) in zip(row_masks, row_boxes):
		xs = split_cols(
			Image.fromarray(
				255 - (255 - np.asarray(thin)) * mask
			)
		)
		for x1, x2 in xs:
			boxes.append((x1, y1, x2, y2))
			masks.append(mask)

	print(len(boxes), "boxes detected.")
	for mask, box in tqdm(zip(masks, boxes), total=len(boxes)):
		img = crop_and_mask(original, box, mask)
		display_image(crop_around_box(draw_boxes(original, [box]), box))
		letter = input()
		if letter:
			img.save(f"{args.output}/{args.prefix}{letter}-{uuid4()}.png")
	print("Done")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--image", type=str, required=True)
	parser.add_argument("--output", type=str, required=True)
	parser.add_argument("--prefix", type=str, default="")
	args = parser.parse_args()
	__main__(args)
