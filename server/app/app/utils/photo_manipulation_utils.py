# Methods Used in manipulating the images

import numpy as np
import cv2

# Returns [processed image, ratio of old/new image]
# Notes: Processing will only work if there is a distinguished background on all four sides
# Will crash if there are less than 4 sides detected.
# Authors: Michaela Chen, Braeden Burgard, and Hans Husurianto
def process_image(image, resolution = 300):
    # Crop
    resized = resize_image(image, resolution)
    thresh = threshold(resized)
    cut = thresh.copy()

    return cut

# Turns the original image to b/w (mostly removes shadows) and removes some noise
# Author: Michaela Chen
def threshold(image):
    # Convert to grayscale, blur to reduce noise, and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.blur(gray, (3,3))
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 10) #src,255=white,mean,binary,kernelsize(odd), kind of like standard dev
    return thresh

# Cleans an image through erosion/dilation
# Author: Michaela Chen
def clean(image):
    se1 = cv2.getStructuringElement(cv2.MORPH_RECT, (5,4))
    se2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3,4))
    mask = cv2.morphologyEx(image, cv2.MORPH_CLOSE, se1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se2)
    return mask

# Cleans an image through erosion/dilation - removes mostly horizontal lines (for lined paper)
# Author: Michaela Chen
def removeHorizontal(image):
    se1 = cv2.getStructuringElement(cv2.MORPH_RECT, (1,6))
    se2 = cv2.getStructuringElement(cv2.MORPH_RECT, (2,3))
    mask = cv2.morphologyEx(image, cv2.MORPH_CLOSE, se1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se2)
    return mask

# Finds the edges of the papers and crops
# Maybe we can do this in real time?? not sure if design team would need to create interface
# Author: Michaela Chen
def crop(image):
    #make a copy of the image to find edges of the paper
    copy = image.copy()
    
    copy = threshold(copy)
    
    #add a border around the copy, so canny can find a closed shape even when paper touches an edge
    top, bottom, left, right = [50]*4
    copy = cv2.copyMakeBorder(copy, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0,0,0])
    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0,0,0])
    #cv2.imshow('expand',copy)
    
    #find edges
    canny = cv2.Canny(copy,100,300) #find all the edges
    contours, hierarchies = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #find the list of edges

    #loop through all contours to find the largest contour aka the paper by area
    if len(contours) != 0:
        contour = 0 
        max_area = 0
        #dots = image.copy()
        #bounds = image.copy()
        count = 0
        number = 0
        for x in contours:
            count+=1
            
            
            
            area = cv2.contourArea(x) #current contour's area
            
            #z,y,w,h = cv2.boundingRect(x) #bounding rectangle of the piece of paper
            #print(count,"rectangle: ", z,y,w,h, "area", area)
            #cv2.rectangle(bounds, (z,y), (z+w, y+h), (0, 255, 0), 2) #draw the rectangle onto original non grayscale image
            #cv2.rectangle(copy, (z,y), (z+w, y+h), (0, 255, 0), 2) #draw the rectangle onto original non grayscale image

            #cv2.imshow('bounds', copy)
            #cv2.imshow('bounds2', image)
            #cv2.drawContours(dots,[x], -1, (0, 255, 0), 3)
            #cv2.imshow('contours', dots)
            #cv2.imshow('rectangles', bounds)
            
            
            #area = cv2.contourArea(x) #current contour's area
            if area > max_area:
                perimeter = cv2.arcLength(x,True)
                approx = cv2.approxPolyDP(x,0.02*perimeter,True) #makes it approx a type of polygon. we want it to return as a quadrilateral
                #test to see if it's a quadrilateral
                #print(count,len(approx))
                if len(approx) == 4:
                    contour = approx
                    max_area = area
                    number = count
                    
    #print("chosen", number)
    #contour returns the four points of the largest contour
    
    #show contours
    #cv2.drawContours(image,[contour], -1, (0, 255, 0), 3) #draw on original non grayscale image for better visual
    #cv2.imshow('contour', image)
    
    #....................................................transform image
    
    #find dst for warp perspective
    x,y,w,h = cv2.boundingRect(contour) #bounding rectangle of the piece of paper
    #cv2.rectangle(image, (x,y), (x+w, y+h), (0, 255, 0), 2) #draw the rectangle onto original non grayscale image
    #cv2.imshow('bounds', image)
    
    #get coordinates from contour for src
    a = contour[0][0]
    b = contour[1][0]
    c = contour[2][0]
    d = contour[3][0]
    
    #match the corners of the paper to the bounding rectangle
    srcCoord = [[a[0],a[1]],[b[0],b[1]],[c[0],c[1]],[d[0],d[1]]]
    dstCoord = [[x,y], [x,y+h], [x+w,y+h], [x+w,y]]
    srcCoord = matchCorners(srcCoord,dstCoord)
    
    #set the variables
    a = srcCoord[0]
    b = srcCoord[1]
    c = srcCoord[2]
    d = srcCoord[3]
    
    #transform
    src = np.float32([(a[0], a[1]), (b[0], b[1]), (c[0], c[1]), (d[0], d[1])])
    dst = np.float32([(0,0), (0,h), (w,h), (w,0)]) #starts at the origin and goes counterclockwise
    m = cv2.getPerspectiveTransform(src, dst) #gets transformation matrix
    warped = cv2.warpPerspective(image, m, (w, h), flags=cv2.INTER_NEAREST)
    #cv2.imshow('warped', warped)
    
    #crop edge a little bit to remove edge pieces
    crop_amount_y = (int)(.01*h)
    crop_amount_x = (int)(.01*w)
    cropped = warped[crop_amount_y:h-crop_amount_y,crop_amount_x:w-crop_amount_x]

    print("*****************************************************************************************************************")

    return cropped

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
        minDistance = np.sqrt((src[0][0]-dst[x][0])*(src[0][0]-dst[x][0])+(src[0][1]-dst[x][1])*(src[0][1]-dst[x][1]))
        for y in range(4):
            distance = np.sqrt((src[y][0]-dst[x][0])*(src[y][0]-dst[x][0])+(src[y][1]-dst[x][1])*(src[y][1]-dst[x][1]))
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
    return cv2.resize(image, (width,width))

def find_square_in_middle(mask):
    # If there are any rows/columns that are totally filled,
    # use them as the starting box, otherwise use the original
    # image frame as the box.
    # Here we assume that the character is more or less in the
    # center of the image. If the box goes through the center
    # this may fail
    if mask[:mask.shape[0]//2,:].all(1).any():
        i = np.where(mask[:mask.shape[0]//2,:].all(1))[0][-1]
    else:
        i = 0
    if mask[mask.shape[0]//2:,:].all(1).any():
        j = np.where(mask[mask.shape[0]//2:,:].all(1))[0][0] + mask.shape[0]//2
    else:
        j = mask.shape[0] - 1
    if mask[:,:mask.shape[1]//2].all(0).any():
        k = np.where(mask[:,:mask.shape[1]//2].all(0))[0][-1]
    else:
        k = 0
    if mask[:,mask.shape[1]//2:].all(0).any():
        l = np.where(mask[:,mask.shape[1]//2:].all(0))[0][0] + mask.shape[1]//2
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
    img_bw = 255*(img <= 128).astype(np.uint8)
    mask = np.zeros((img.shape[0] + 2, img.shape[1] + 2), dtype=np.uint8)

    # Floodfill all dark pixels near borders as they are likely part of the box
    # If the character goes off the edge of the image, this is going to cause problems
    for i in range(img_bw.shape[0]):
        if img_bw[i, 0]:
            cv2.floodFill(img_bw, mask, (0, i), 128)
        if img_bw[i, -1]:
            cv2.floodFill(img_bw, mask, (img_bw.shape[1]-1, i), 128)
    for j in range(img_bw.shape[1]):
        if img_bw[0, j]:
            cv2.floodFill(img_bw, mask, (j, 0), 128)
        if img_bw[-1, j]:
            cv2.floodFill(img_bw, mask, (j, img_bw.shape[0]-1), 128)

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
def detect_gridlines(processed_image, template):
    #sum up the total number of black pixels in each row/column
    sumhorizontal = np.zeros(processed_image.shape[0])
    sumvertical = np.zeros(processed_image.shape[1])
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
    horizontal_interval = int(processed_image.shape[0] / 5 / horizontal_lines)
    min_horizontal_positions = np.zeros(horizontal_lines)
    for line in range(horizontal_lines):
        min_index = np.argmin(sumhorizontal)
        min_horizontal_positions[line] = min_index
        
        if min_index < horizontal_interval:
            i = 0
        else:
            i = min_index - horizontal_interval
        while i <= min_index + horizontal_interval and i < len(sumhorizontal):
            sumhorizontal[i] = 999
            i += 1
            
    vertical_lines = len(template[0])+1
    vertical_interval = int(processed_image.shape[1] / 5 / vertical_lines)
    min_vertical_positions = np.zeros(vertical_lines)
    for line in range(vertical_lines):
        min_index = np.argmin(sumvertical)
        min_vertical_positions[line] = min_index
        
        if min_index < vertical_interval:
            i = 0
        else:
            i = min_index - vertical_interval
        while i <= min_index + vertical_interval and i < len(sumvertical):
            sumvertical[i] = 999
            i += 1

    min_horizontal_positions = np.sort(min_horizontal_positions).astype(int)
    min_vertical_positions = np.sort(min_vertical_positions).astype(int)
    score = sum(min_horizontal_positions) + sum(min_vertical_positions)
    return [min_horizontal_positions,min_vertical_positions,score]

#Returns [cut images, flattened template]
# Function to cut out the individual symbols from the gridlines
# Author: Braeden Burgard
def cut_image(image, processed_image, template):
    h_ratio = image.shape[1] / processed_image.shape[1]
    v_ratio = image.shape[0] / processed_image.shape[0]
    [horizontal_gridlines, vertical_gridlines, score] = detect_gridlines(processed_image,template)
    cut_images = []
    for h in range(len(horizontal_gridlines)-1):
        for v in range(len(vertical_gridlines)-1):
            cut_images.append(
                image[int(horizontal_gridlines[h]*v_ratio) : int(horizontal_gridlines[h+1]*v_ratio),
                      int(vertical_gridlines[v]*h_ratio)   : int(vertical_gridlines[v+1]*h_ratio)])
    flattened_template = tuple(np.asarray(template).flatten())
    return [cut_images,flattened_template]

# Returns an image with the gridlines drawn in. For debugging purposes
# Author: Braeden Burgard
def dev_grid_picture(processed_image, horizontal_lines, vertical_lines):
    gridded_image = np.copy(processed_image)
    for i in horizontal_lines:
        for j in range(gridded_image.shape[1]):
            gridded_image[i][j] = 130
    for j in vertical_lines:
        for i in range(gridded_image.shape[0]):
            gridded_image[i][j] = 130
    return gridded_image

# Create aliases for the *_image functions (ie. cut_image = cut)
# Eventually remove the `_image` suffix, but for now just create an alias
for name, func in list(locals().items()):
    if name.endswith("_image"):
        short_name = name[:name.rindex("_image")]
        locals()[short_name] = func
