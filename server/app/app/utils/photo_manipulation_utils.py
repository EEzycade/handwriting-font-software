# For now, this will consist of many different methods so we can easily change/exchange them
# Before submission, we might want to compress them into only the methods we need

from flask import flash
from cv2 import resize,cvtColor,threshold,blur,adaptiveThreshold,getStructuringElement,morphologyEx,COLOR_BGR2GRAY,THRESH_BINARY,ADAPTIVE_THRESH_MEAN_C,MORPH_RECT,MORPH_ELLIPSE,MORPH_CLOSE,MORPH_OPEN
from imutils import resize
from numpy import zeros,argmin,sort,sum,asarray,copy,ndarray

template_symbols_dict = {
  "english_lower_case_letters": [["a","b","c","d"],
                                 ["e","f","g","h"],
                                 ["i","j",None,None]]
}

#Returns [processed image, ratio of old/new image]
def process_image(image):
    resized = resize(image, width=100)
    ratio = image.shape[0] / float(resized.shape[0])
    
    #gray = cvtColor(resized, COLOR_BGR2GRAY)
    #thresh = threshold(gray, 200, 255, THRESH_BINARY)[1]
    
    #threshold
    gray = cvtColor(image, COLOR_BGR2GRAY)
    blurred = blur(gray, (3,3))
    thresh = adaptiveThreshold(blurred,255,ADAPTIVE_THRESH_MEAN_C,THRESH_BINARY,31,10)
    
    #remove noise
    se1 = getStructuringElement(MORPH_RECT, (5,4))
    se2 = getStructuringElement(MORPH_ELLIPSE, (3,4))
    mask = morphologyEx(thresh, MORPH_CLOSE, se1)
    mask = morphologyEx(mask, MORPH_OPEN, se2)
    
    cut = mask.copy()
    return [cut,ratio]

# Returns [horizontal gridlines, vertical gridlines, score]
# Score is used to judge how well the gridlines were found. It is not used at the moment.
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
def cut_image(image, processed_image, template_type, ratio):
    template = template_symbols_dict[template_type]
    grid_tuple = detect_gridlines(processed_image,template_type)
    cut_images = []
    for h in range(len(grid_tuple[0])-1):
        for v in range(len(grid_tuple[1])-1):
            cut_images.append(image[int(grid_tuple[0][h]*ratio) : int(grid_tuple[0][h+1]*ratio), int(grid_tuple[1][v]*ratio) : int(grid_tuple[1][v+1]*ratio)])
    flattened_template = tuple(asarray(template).flatten())
    return [cut_images,flattened_template]

# Returns an image with the gridlines drawn in. For debugging purposes
def dev_grid_picture(processed_image, horizontal_lines, vertical_lines):
    gridded_image = copy(processed_image)
    for i in horizontal_lines:
        for j in range(gridded_image.shape[1]):
            gridded_image[i][j] = 130
    for j in vertical_lines:
        for i in range(gridded_image.shape[0]):
            gridded_image[i][j] = 130
    return gridded_image