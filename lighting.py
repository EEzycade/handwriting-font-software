import sys
import cv2 as cv

def __main__():
    if len(sys.argv) != 2:
        print("gimme the image path")
        return

    path = sys.argv[1]
    img = cv.imread(path)
    cv.imshow('original_image', img)

    new_img = manipulate(img)

    cv.imshow('new_image', new_img)
    cv.waitKey(0)

def manipulate(image):
    #convert to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    #cv.imshow('gray', gray)

    #blur to reduce noise
    blur = cv.blur(gray, (3,3))
    #cv.imshow('blur', blur)

    #thresholding (!!!)
    thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,31,10) #src,255=white,mean,binary,kernelsize(odd),kinda like standard dev
    #cv.imshow('threshold', thresh)

    return thresh

if __name__ == "__main__":
    __main__()