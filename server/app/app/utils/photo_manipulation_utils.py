# Methods Used in manipulating the images

import math
from flask import flash
from cv2 import resize,cvtColor,threshold,blur,adaptiveThreshold,getStructuringElement,morphologyEx,findContours,contourArea,arcLength,approxPolyDP,drawContours,boundingRect,rectangle,getPerspectiveTransform,warpPerspective,imshow,floodFill,Canny,COLOR_BGR2GRAY,THRESH_BINARY,ADAPTIVE_THRESH_MEAN_C,MORPH_RECT,MORPH_ELLIPSE,MORPH_CLOSE,MORPH_OPEN,RETR_EXTERNAL,CHAIN_APPROX_SIMPLE,INTER_NEAREST
from imutils import resize
from numpy import zeros,argmin,sort,sum,asarray,copy,ndarray,float32,uint8,where
from app.utils.constants import template_symbols_dict

# Returns [processed image, ratio of old/new image]
# Notes: Processing will only work if there is a distinguished background on all four sides
# Will crash if there are less than 4 sides detected.
# Authors: Michaela Chen, Braeden Burgard, and Hans Husurianto
def process_image(image):
    #resized = resize(image, width=100)
    #ratio = image.shape[0] / float(resized.shape[0])

    # Threshold
    # thresh = threshold(resized)
    # Remove noise
    #mask = clean(thresh)

    # Crop
    img = crop(image)
    resized = resize(img, width=100)
    ratio = img.shape[0] / float(resized.shape[0])

    #img = threshold(resized)
    #img = clean(img)
    cut = img.copy()

    return [cut,ratio]

# Turns the original image to b/w (mostly removes shadows) and removes some noise
# Author: Michaela Chen
def threshold(image):
    # Convert to grayscale, blur to reduce noise, and threshold
    gray = cvtColor(image, COLOR_BGR2GRAY)
    blurred = blur(gray, (3,3))
    thresh = adaptiveThreshold(blurred, 255, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, 31, 10) #src,255=white,mean,binary,kernelsize(odd), kind of like standard dev
    return thresh

# Cleans an image through erosion/dilation
# Author: Michaela Chen
def clean(image):
    se1 = getStructuringElement(MORPH_RECT, (5,4))
    se2 = getStructuringElement(MORPH_RECT, (3,4))
    mask = morphologyEx(image, MORPH_CLOSE, se1)
    mask = morphologyEx(mask, MORPH_OPEN, se2)
    return mask

# Cleans an image through erosion/dilation - removes mostly horizontal lines (for lined paper)
# Author: Michaela Chen
def removeHorizontal(image):
    se1 = getStructuringElement(MORPH_RECT, (1,6))
    se2 = getStructuringElement(MORPH_RECT, (2,3))
    mask = morphologyEx(image, MORPH_CLOSE, se1)
    mask = morphologyEx(mask, MORPH_OPEN, se2)
    return mask

# Finds the edges of the papers and crops
# Maybe we can do this in real time?? not sure if design team would need to create interface
# Author: Michaela Chen
def crop(image):
    # Make a copy of the image
    copy = image.copy()
    
    # Grayscale and blur the image
    copy = threshold(copy)

    # Find edges
    canny = Canny(copy,100,300) # Find all the edges
    contours, hierarchies = findContours(canny, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE) #find the list of edges

    # Loop through all contours to find the largest contour aka the paper by area
    if len(contours) != 0:
        contour = 0 
        max_area = 0
        for x in contours:
            area = contourArea(x) # Current contour's area
            if area > max_area:
                perimeter = arcLength(x,True)
                approx = approxPolyDP(x,0.02*perimeter,True) # Makes it approx a type of polygon. we want it to return as a quadrilateral
                # Test to see if it's a quadrilateral
                if len(approx) == 4:
                    contour = approx
                    max_area = area
    # Contour returns the four points of the largest contour
    
    # Show contours
    drawContours(image,[contour], -1, (0, 255, 0), 3) # Draw on original non grayscale image for better visual
    
    ## Transform Image
    
    # Find dst for warp perspective
    x,y,w,h = boundingRect(contour) # Bounding rectangle of the piece of paper
    rectangle(image, (x,y), (x+w, y+h), (0, 255, 0), 2) # Draw the rectangle onto original non grayscale image
    
    # Get coordinates from contour for src
    a = contour[0][0]
    b = contour[1][0]
    c = contour[2][0]
    d = contour[3][0]
    
    # Match the corners of the paper to the bounding rectangle
    srcCoord = [[a[0],a[1]],[b[0],b[1]],[c[0],c[1]],[d[0],d[1]]]
    dstCoord = [[x,y], [x,y+h], [x+w,y+h], [x+w,y]]
    srcCoord = matchCorners(srcCoord,dstCoord)
    
    # Set the variables
    a = srcCoord[0]
    b = srcCoord[1]
    c = srcCoord[2]
    d = srcCoord[3]
    
    # Transform the image
    src = float32([(a[0], a[1]), (b[0], b[1]), (c[0], c[1]), (d[0], d[1])])
    dst = float32([(0,0), (0,h), (w,h), (w,0)]) # Starts at the origin and goes counterclockwise
    m = getPerspectiveTransform(src, dst) # Gets transformation matrix
    warped = warpPerspective(copy, m, (w, h), flags=INTER_NEAREST)

    return warped

# Finds the corners of the paper and matches them to the bounding rectangle
# Author: Michaela Chen
def matchCorners(src,dst):
    #print(src)  
    #print(dst)
    result = []
    for x in range(4):
        #print("x: " + str(x))
        #print(dst[x])
        index = 0
        minDistance = math.sqrt((src[0][0]-dst[x][0])*(src[0][0]-dst[x][0])+(src[0][1]-dst[x][1])*(src[0][1]-dst[x][1]))
        for y in range(4):
            distance = math.sqrt((src[y][0]-dst[x][0])*(src[y][0]-dst[x][0])+(src[y][1]-dst[x][1])*(src[y][1]-dst[x][1]))
            #print(src) 
            #print("y: " + str(y))
            if (distance < minDistance):
                minDistance = distance
                index = y
        #print(src[index])
        #print()
        result.append(src[index])
    #print(result)
    return result

# Resize the image for faster processing in detecting gridlines
def resize_image(image, width=100):
    return (resize(image, width), image.shape[1]/width)

def find_square_in_middle(mask):
    # If there are any rows/columns that are totally filled,
    # use them as the starting box, otherwise use the original
    # image frame as the box.
    # Here we assume that the character is more or less in the
    # center of the image. If the box goes through the center
    # this may fail
    if mask[:mask.shape[0]//2,:].all(1).any():
        i = where(mask[:mask.shape[0]//2,:].all(1))[0][-1]
    else:
        i = 0
    if mask[mask.shape[0]//2:,:].all(1).any():
        j = where(mask[mask.shape[0]//2:,:].all(1))[0][0] + mask.shape[0]//2
    else:
        j = mask.shape[0] - 1
    if mask[:,:mask.shape[1]//2].all(0).any():
        k = where(mask[:,:mask.shape[1]//2].all(0))[0][-1]
    else:
        k = 0
    if mask[:,mask.shape[1]//2:].all(0).any():
        l = where(mask[:,mask.shape[1]//2:].all(0))[0][0] + mask.shape[1]//2
    else:
        l = mask.shape[1] - 1

    # Greedily shrink the frame to get rid of the box as best as possible
    while i < j and k < l and mask[i:j, k:l].any():
        top   = mask[i, k:l].mean()
        bot   = mask[j, k:l].mean()
        left  = mask[i:j, k].mean()
        right = mask[i:j, l].mean()
        m = max(top, bot, left, right)
        if m == top:
            i += 1
        elif m == bot:
            j -= 1
        elif m == left:
            k += 1
        elif m == right:
            l -= 1
        else: assert False
    return i, j, k, l

def unbox_image(img):
    """Remove the box from the edges of the image

    If the character goes out of the image bounds there's gonna be a problem
    """
    img_bw = 255*(img <= 128).astype(uint8)
    mask = zeros((img.shape[0] + 2, img.shape[1] + 2), dtype=uint8)

    # Floodfill all dark pixels near borders as they are likely part of the box
    # If the character goes off the edge of the image, this is going to cause problems
    for i in range(img_bw.shape[0]):
        if img_bw[i, 0]:
            floodFill(img_bw, mask, (0, i), 128)
        if img_bw[i, -1]:
            floodFill(img_bw, mask, (img_bw.shape[1]-1, i), 128)
    for j in range(img_bw.shape[1]):
        if img_bw[0, j]:
            floodFill(img_bw, mask, (j, 0), 128)
        if img_bw[-1, j]:
            floodFill(img_bw, mask, (j, img_bw.shape[0]-1), 128)

    i, j, k, l = find_square_in_middle(mask[1:-1,1:-1])
    if i >= j or k >= l:
        print("Failed to remove box! Returning original image. "
              "This is likely because the box is not positioned in the image correctly. "
              "Check the cut images to debug.")
        return img
    #assert i < j and k < l
    return img[i:j, k:l]

# Returns [horizontal gridlines, vertical gridlines, score]
# Score is used to judge how well the gridlines were found. It is not used at the moment.
# Author: Braeden Burgard
def detect_gridlines(processed_image, template_type):
    template = template_symbols_dict[template_type]
    #sum up the total number of black pixels in each row/column
    sumhorizontal = zeros(processed_image.shape[0])
    sumvertical = zeros(processed_image.shape[1])
    for i in range(0,int(processed_image.shape[0])):
        for j in range(0,int(processed_image.shape[1])):
            sumhorizontal[i] += processed_image[i][j]/255
            sumvertical[j] += processed_image[i][j]/255
            
    #Get rid of sums that are TOO low. They're probably noise, not grid lines
    for i in range(len(sumhorizontal)):
        if sumhorizontal[i] < .25 * processed_image.shape[1]:
            sumhorizontal[i] = 999
    for i in range(len(sumvertical)):
        if sumvertical[i] < .25 * processed_image.shape[0]:
            sumvertical[i] = 999
                    
    horizontal_lines = len(template)+1
    horizontal_interval = int(processed_image.shape[0] / 2 / horizontal_lines)
    min_horizontal_positions = zeros(horizontal_lines)
    for line in range(horizontal_lines):
        min_index = argmin(sumhorizontal)
        min_horizontal_positions[line] = min_index
        
        if min_index < horizontal_interval:
            i = 0
        else:
            i = min_index - horizontal_interval
        while i <= min_index + horizontal_interval and i < len(sumhorizontal):
            sumhorizontal[i] = 999
            i += 1
            
    vertical_lines = len(template[0])+1
    vertical_interval = int(processed_image.shape[1] / 2 / vertical_lines)
    min_vertical_positions = zeros(vertical_lines)
    for line in range(vertical_lines):
        min_index = argmin(sumvertical)
        min_vertical_positions[line] = min_index
        
        if min_index < vertical_interval:
            i = 0
        else:
            i = min_index - vertical_interval
        while i <= min_index + vertical_interval and i < len(sumvertical):
            sumvertical[i] = 999
            i += 1

    min_horizontal_positions = sort(min_horizontal_positions).astype(int)
    min_vertical_positions = sort(min_vertical_positions).astype(int)
    score = sum(min_horizontal_positions) + sum(min_vertical_positions)
    return [min_horizontal_positions,min_vertical_positions,score]

#Returns [cut images, flattened template]
# Function to cut out the individual symbols from the gridlines
# Author: Braeden Burgard
def cut_image(image, processed_image, template_type, ratio):
    ratio = image.shape[1] / processed_image.shape[1]
    template = template_symbols_dict[template_type]
    grid_tuple = detect_gridlines(processed_image,template_type)
    cut_images = []
    for h in range(len(grid_tuple[0])-1):
        for v in range(len(grid_tuple[1])-1):
            cut_images.append(image[int(grid_tuple[0][h]*ratio) : int(grid_tuple[0][h+1]*ratio), int(grid_tuple[1][v]*ratio) : int(grid_tuple[1][v+1]*ratio)])
    flattened_template = tuple(asarray(template).flatten())
    return [cut_images,flattened_template]

# Returns an image with the gridlines drawn in. For debugging purposes
# Author: Braeden Burgard
def dev_grid_picture(processed_image, horizontal_lines, vertical_lines):
    gridded_image = copy(processed_image)
    for i in horizontal_lines:
        for j in range(gridded_image.shape[1]):
            gridded_image[i][j] = 130
    for j in vertical_lines:
        for i in range(gridded_image.shape[0]):
            gridded_image[i][j] = 130
    return gridded_image