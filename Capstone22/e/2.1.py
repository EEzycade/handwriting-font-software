# importing modules

import cv2

 import pytesseract

# reading image using opencv

 image = cv2.imread(sample_image.png’)

 #converting image into gray scale image

 gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

 # converting it to binary image by Thresholding

 # this step is require if you have colored image because if you skip this part
 # then tesseract won't able to detect text correctly and this will give incorrect result

threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

 # display image

 cv2.imshow(‘threshold image’, threshold_img)

 # Maintain output window until user presses a key

 cv2.waitKey(0)

 # Destroying present windows on screen

 cv2.destroyAllWindows()

#configuring parameters for tesseract

 custom_config = r'--oem 3 --psm 6'

 # now feeding image to tesseract

 details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang=’eng’)

 print(details.keys())

  total_boxes = len(details['text'])

 for sequence_number in range(total_boxes):

 	if int(details['conf'][sequence_number]) >30:

		(x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number],  details['height'][sequence_number])

 		threshold_img = cv2.rectangle(threshold_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

 # display image

 cv2.imshow(‘captured text’, threshold_img)

 # Maintain output window until user presses a key

 cv2.waitKey(0)

 # Destroying present windows on screen

 cv2.destroyAllWindows()

 parse_text = []

 word_list = []

 last_word = ''

 for word in details['text']:

     if word!='':

        word_list.append(word)

        last_word = word

    if (last_word!='' and word == '') or (word==details['text'][-1]):

         parse_text.append(word_list)

         word_list = []

         import csv

 with open(result_text.txt',  'w', newline="") as file:
   csv.writer(file, delimiter=" ").writerows(parse_text)
