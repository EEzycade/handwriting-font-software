import sys
from turtle import distance
import cv2 as cv
from cv2 import sqrt
import numpy as np
import math

def __main__():
    if len(sys.argv) != 2:
        print("Please add an image file path.")
        return

    path = sys.argv[1]
    img = cv.imread(path)
    #print(type(img))

    if img is None:
        print("The image file does not exist.")
        return
    
    #resized = cv.resize(img, width=300)
    ratio = 400/img.shape[1] # [0] = height, [1] = width, [2] = # of channels
    #img = cv.resize(img, ((int)(img.shape[1]*ratio), (int)(img.shape[0]*ratio)))
    
    cv.imshow('original_image', img)
    #image manipulation
    img = crop(img)
    img = threshold(img)
    #img = clean(img)

    cv.imshow('new_image', img)
    cv.waitKey(0)
    #print(type(img))

#turns the original image to b/w (mostly removes shadows) and removes some noise
def threshold(image):
#def threshold(image, blur1,blur2,thresh1,thresh2):
    #convert to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    #cv.imshow('gray', gray)

    #blur to reduce noise
    #blur = cv.blur(gray, (1,31))
    blur = cv.blur(gray, (5,5))
    cv.imshow('blur', blur)

    #thresholding
    #ret,thresh = cv.threshold(blur,(int)(cv.mean(blur)[0]*2),255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,31,10) #src,255=white,mean,binary,kernelsize(odd),kinda like standard dev
    cv.imshow('threshold', thresh)

    return thresh

#cleans an image through erosion/dilation
def clean(image):
#def clean(image,se1a,se1b,se2a,se2b):
    #cv.imshow('before', image)

    se1 = cv.getStructuringElement(cv.MORPH_RECT, (1,1)) #if we want, these values can be adjusted by the user
    #se1 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
    se2 = cv.getStructuringElement(cv.MORPH_RECT, (1,1))
    #se2 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,4))
    mask = cv.morphologyEx(image, cv.MORPH_CLOSE, se1)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, se2)

    #cv.imshow('mask', mask)

    return mask

#cleans an image through erosion/dilation - removes mostly horizontal lines (for lined paper)
def removeHorizontal(image):
    #cv.imshow('before', image)

    se1 = cv.getStructuringElement(cv.MORPH_RECT, (1,6))
    se2 = cv.getStructuringElement(cv.MORPH_RECT, (2,3))
    mask = cv.morphologyEx(image, cv.MORPH_CLOSE, se1)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, se2)

    #cv.imshow('mask', mask)

    return mask

#finds the edges of the papers and crops
#maybe we can do this in real time?? not sure if design team would need to create interface
def crop(image):
    #make a copy of the image to find edges of the paper
    copy = image.copy()
    
    #grayscale and blur the copy
    copy = cv.cvtColor(copy, cv.COLOR_BGR2GRAY)
    copy = cv.blur(copy, (5,5))
    #cv.imshow('blur',copy)
    #print(cv.mean(copy))
    ret,copy = cv.threshold(copy,(int)(cv.mean(copy)[0]*.3),255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    #cv.imshow('threshold',copy)
    
    #add a border around the copy, so canny can find a closed shape even when paper touches an edge
    top, bottom, left, right = [50]*4
    copy = cv.copyMakeBorder(copy, top, bottom, left, right, cv.BORDER_CONSTANT, value=[0,0,0])
    image = cv.copyMakeBorder(image, top, bottom, left, right, cv.BORDER_CONSTANT, value=[0,0,0])
    #cv.imshow('expand',copy)
    
    #find edges
    canny = cv.Canny(copy,100,300) #find all the edges
    contours, hierarchies = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) #find the list of edges

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
            
            
            
            area = cv.contourArea(x) #current contour's area
            
            #z,y,w,h = cv.boundingRect(x) #bounding rectangle of the piece of paper
            #print(count,"rectangle: ", z,y,w,h, "area", area)
            #cv.rectangle(bounds, (z,y), (z+w, y+h), (0, 255, 0), 2) #draw the rectangle onto original non grayscale image
            #cv.rectangle(copy, (z,y), (z+w, y+h), (0, 255, 0), 2) #draw the rectangle onto original non grayscale image

            #cv.imshow('bounds', copy)
            #cv.imshow('bounds2', image)
            #cv.drawContours(dots,[x], -1, (0, 255, 0), 3)
            #cv.imshow('contours', dots)
            #cv.imshow('rectangles', bounds)
            
            
            #area = cv.contourArea(x) #current contour's area
            if area > max_area:
                perimeter = cv.arcLength(x,True)
                approx = cv.approxPolyDP(x,0.02*perimeter,True) #makes it approx a type of polygon. we want it to return as a quadrilateral
                #test to see if it's a quadrilateral
                #print(count,len(approx))
                if len(approx) == 4:
                    contour = approx
                    max_area = area
                    number = count
                    
    #print("chosen", number)
    #contour returns the four points of the largest contour
    
    #show contours
    #cv.drawContours(image,[contour], -1, (0, 255, 0), 3) #draw on original non grayscale image for better visual
    #cv.imshow('contour', image)
    
    #....................................................transform image
    
    #find dst for warp perspective
    x,y,w,h = cv.boundingRect(contour) #bounding rectangle of the piece of paper
    #cv.rectangle(image, (x,y), (x+w, y+h), (0, 255, 0), 2) #draw the rectangle onto original non grayscale image
    #cv.imshow('bounds', image)
    
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
    m = cv.getPerspectiveTransform(src, dst) #gets transformation matrix
    warped = cv.warpPerspective(image, m, (w, h), flags=cv.INTER_NEAREST)
    #cv.imshow('warped', warped)
    
    #crop edge a little bit to remove edge pieces
    crop_amount_y = (int)(.01*h)
    crop_amount_x = (int)(.01*w)
    cropped = warped[crop_amount_y:h-crop_amount_y,crop_amount_x:w-crop_amount_x]
    
    cv.imshow('cropped', cropped)
    
    return cropped

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
        

if __name__ == "__main__":
    __main__()