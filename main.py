from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import random as rng

source_window = 'Dices'
grayscale = 'Grayed'
canny_window = 'Canny Applied'
threshold_window = 'Threshold Applied'

parser = argparse.ArgumentParser(description='Code for Finding contours in your image tutorial.')
parser.add_argument('--input', help='Path to input image.')
args = parser.parse_args()

src = cv.imread(args.input)
src = cv.resize(src, (800, 600))

if src is None:
    print('Could not open or find the image:', args.input)
    exit(0)

# Convert image to gray
src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
src_gray = cv.medianBlur(src_gray, 5)

# Thresholding
ret, thresh = cv.threshold(src_gray, 130, 255, cv.THRESH_BINARY)
#thresh = cv.adaptiveThreshold(src_gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 27, 1)
canny = cv.Canny(thresh, 2, 4, 10)
canny = cv.blur(canny, (3, 3))

# Finding contours
contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# Getting bounding rectangles and circles
contours_poly = [None]*len(contours)
boundRect = [None]*len(contours)
centers = [None]*len(contours)
radius = [None]*len(contours)
for i, c in enumerate(contours):
    contours_poly[i] = cv.approxPolyDP(c, 3, True)
    boundRect[i] = cv.boundingRect(contours_poly[i])
    centers[i], radius[i] = cv.minEnclosingCircle(contours_poly[i])

dices = []

# Drawing contorus and bounding rectangles
for i in range(len(contours)):
    color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
    cv.drawContours(src, contours_poly, i, color)
    if (cv.contourArea(contours[i]) > 700):
        dices.append(src_gray[boundRect[i][1] : boundRect[i][1] + boundRect[i][3], boundRect[i][0] : boundRect[i][0] + boundRect[i][2]])
        cv.rectangle(src, (int(boundRect[i][0]), int(boundRect[i][1])), \
              (int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), color, 2)

det = cv.SimpleBlobDetector().create()
k = 1
for i in dices:
    i = cv.adaptiveThreshold(i, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 17, 1)
    cv.imshow(str(k), i)
    print(k, len(det.detect(i)))
    k += 1


# Create Windows
cv.namedWindow(source_window, cv.WINDOW_NORMAL)
cv.resizeWindow(source_window, 800, 600)
cv.imshow(source_window, src)

cv.namedWindow(grayscale, cv.WINDOW_NORMAL)
cv.resizeWindow(grayscale, 800, 600)
cv.imshow(grayscale, src_gray)

cv.namedWindow(threshold_window, cv.WINDOW_NORMAL)
cv.resizeWindow(threshold_window, 800, 600)
cv.imshow(threshold_window, thresh)

cv.namedWindow(canny_window, cv.WINDOW_NORMAL)
cv.resizeWindow(canny_window, 800, 600)
cv.imshow(canny_window, canny)

cv.waitKey()