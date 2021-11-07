import sys
import cv2 as cv
import numpy as np

def __main__():
    if len(sys.argv) != 2:
        print("Please add an image file path.")
        return

    path = sys.argv[1]
    img = cv.imread(path)

    if img is None:
        print("The image file does not exist.")
        return
        
    cv.imshow('original_image', img)

    #image manipulation
    img = threshold(img)
    img = clean(img)

    cv.imshow('new_image', img)
    cv.waitKey(0)

#turns the original image to b/w (mostly removes shadows) and removes some noise
def threshold(image):
    #convert to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    #cv.imshow('gray', gray)

    #blur to reduce noise
    blur = cv.blur(gray, (3,3))
    #cv.imshow('blur', blur)

    #thresholding
    thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,31,10) #src,255=white,mean,binary,kernelsize(odd),kinda like standard dev
    #cv.imshow('threshold', thresh)

    return thresh

#cleans an image through erosion/dilation
def clean(image):
    #cv.imshow('before', image)

    se1 = cv.getStructuringElement(cv.MORPH_RECT, (5,4))
    #se1 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
    #se2 = cv.getStructuringElement(cv.MORPH_RECT, (2,3))
    se2 = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,4))
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

if __name__ == "__main__":
    __main__()