# importing the libraries
import cv2
import pytesseract

# seting the path of pytesseract exe
# you have to write the location of
# on which your tesseract was installed
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.1/bin/tesseract'

# Now we will read the image in our program
# you have to put your image path in place of photo.jpg
img = cv2.imread('/Users/raghavbansal/Downloads/my.png')

# Our image will read as BGR format,
# So we will convert in RGB format because
# tesseract can only read in RGB format
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
cv2.imshow('Result',img)

#Detecting characters
hImg,wImg,_ =img.shape
pytesseract.image_to_boxes(img)
for b in boxes.splitlines():
    b = b.split('')
    x,y,w,h = int(b[1]),int(b[2]),int(b[3]),int(b[4])
    cv2.rectangle(img,(x,hImg-y),(w,hImg-h),(0,0,255),1)
    cv2.putText(img,b[0],(x,hImg-y),cv2.FONT_HERSHEY_SIMPLEX,1,(50,50))
# For getting the text and number from image
print(pytesseract.image_to_string(img))


# For displaying the orignal image
cv2.imshow("result", img)
cv2.waitKey(0)
