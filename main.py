from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import math

def distCircle(circle, circle2):
    distx = circle[0] - circle2[0] if circle[0] > circle2[0] else circle2[0] - circle[0]
    disty = circle[1] - circle2[1] if circle[1] > circle2[1] else circle2[1] - circle[1]
    distance = math.sqrt(pow(distx,2) + pow(disty,2))
    return distance


source_window = 'Dices'
grayscale = 'Grayed'
canny_window = 'Canny Applied'
threshold_window = 'Threshold Applied'

parser = argparse.ArgumentParser(description='Code for Finding contours in your image tutorial.')
parser.add_argument('-i', '--input', help='Path to input image.', nargs='+')
parser.add_argument('-w', '--write', help='Images will be saved in folder DonePhotos.', action='store_true')
parser.add_argument('-d', '--debug', help='Less info will be printed', action='store_false')
args = parser.parse_args()
namePh = 1

srcs = []
for i in args.input:
    srcs.append(cv.imread(i))

# Run program for every input photo
for src in srcs:
    if src is None:
        print('Could not open or find the image:', args.input)
        continue

    # Convert image to gray
    src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    src_gray = cv.blur(src_gray, (3,3))
    src_gray = cv.medianBlur(src_gray, 21)

    # Thresholding
    _, thresh = cv.threshold(src_gray, 50, 255, cv.THRESH_BINARY)

    # Fill corners of image with white
    cv.floodFill(thresh, np.zeros((len(thresh)+2, len(thresh[0])+2), np.uint8), (0, 0), 255)
    cv.floodFill(thresh, np.zeros((len(thresh)+2, len(thresh[0])+2), np.uint8), (len(thresh[0])-1, len(thresh)-1), 255)
    cv.floodFill(thresh, np.zeros((len(thresh)+2, len(thresh[0])+2), np.uint8), (0, len(thresh) - 1), 255)
    cv.floodFill(thresh, np.zeros((len(thresh)+2, len(thresh[0])+2), np.uint8), (len(thresh[0])-1, 0), 255)

    # Get canny for edges
    canny = cv.Canny(thresh, 2, 4)
    canny = cv.blur(canny, (3, 3))

    # Finding contours
    contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv.approxPolyDP(cnt, .03 * cv.arcLength(cnt, True), True)
        print(len(approx))
        if len(approx) == 3:
            print("triangle")
            #cv.drawContours(src, [cnt], 0, (122, 212, 78), -1)
        elif len(approx) == 4:
            print("square")
            #cv.drawContours(src, [cnt], 0, (94, 234, 255), -1)
        elif len(approx) >= 7:
            area = cv.contourArea(cnt)
            (cx, cy), radius = cv.minEnclosingCircle(cnt)
            circleArea = radius * radius * np.pi
            print(circleArea)
            print(area)
            if abs(circleArea - area) < 2/5*area:
                cv.drawContours(src, [cnt], 0, (220, 152, 91), -1)


    # Create Windows
    if args.debug:
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

    if args.write:
        cv.imwrite("DonePhotos/ph" + str(namePh) + ".jpg", src)
        print("Saved file: DonePhotos/ph" + str(namePh) + ".jpg")
        namePh += 1