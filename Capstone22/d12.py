import cv2

BLACK_THRESHOLD = 200
THIN_THRESHOLD = 10

im = cv2.imread('IMG_0832.png', 0)


ret, thresh = cv2.threshold(im, 150, 255, cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
idx = 0
for cnt in contours:
    idx += 1
    x, y, w, h = cv2.boundingRect(cnt)
    roi = im[y:y + h, x:x + w]
    if h < THIN_THRESHOLD or w < THIN_THRESHOLD:
        continue
    cv2.imwrite(str(idx) + '.png', roi)
    cv2.rectangle(im, (x, y), (x + w, y + h), (200, 0, 0), 2)
cv2.imshow('img', im)
cv2.waitKey(0)
