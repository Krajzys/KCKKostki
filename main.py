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

    # Finding circles
    circles = cv.HoughCircles(src_gray, cv.HOUGH_GRADIENT, 2, 100, param1 = 35, param2 = 30, minRadius = 30, maxRadius = 70)
    #circles = cv.HoughCircles(src_gray, cv.HOUGH_GRADIENT, 1.8, 100, param1 = 35, param2=25, minRadius=20, maxRadius=75)

    if circles is not None:
        circles = np.uint16(np.around(circles))

        betterCircles = []

        # Check to find right circles and append them to betterCircles
        index_k = 0
        for i in circles[0, :]:
            my_x = i[0] - i[2]
            my_y = i[1] - i[2]
            rect = cv.rectangle(src, (my_x, my_y), (my_x + i[2]*2, my_y + i[2]*2), (255, 0, 0), 4)
            #cv.circle(src, (i[0], i[1]), i[2], (0, 0, 255), 2)
            if np.mean(thresh[my_y: my_y + i[2] * 2, my_x: my_x + i[2] * 2]) < 100:
                #cv.putText(src, "Kropka" + str(index_k), (my_x, my_y), cv.FONT_HERSHEY_PLAIN, 4, (255, 255, 0), 10)
                betterCircles.append(i)
                index_k += 1
                #cv.circle(src, (i[0], i[1]), i[2], (0, 255, 0), 2)
                #cv.circle(src, (i[0], i[1]), 2, (0, 0, 255), 3)


        ungrouped = betterCircles[:]
        grouped = []
        groups = []

        # Grouping of dots
        for ind in range(len(ungrouped)):
            circle = ungrouped[ind]
            if ind in grouped:
                continue
            grouped.append(ind)
            group = [ind]
            groups.append(group)
            radius = int(circle[2]*7.4)
            for i in range(len(ungrouped)):
                if ind != i and i not in grouped: # circle is not the same and isnt yet grouped
                    circle2 = ungrouped[i]
                    #print("Indeksy", ind, i)
                    #print("X Y", circle[0], circle[1], circle2[0], circle2[1])
                    if distCircle(circle, circle2) <= radius:
                        grouped.append(i)
                        groups[-1].append(i)
                        #group.append(i)


        if args.debug:
            print(groups)
        # Draw rectangles around dices
        for i in groups:
            minx = 10000
            maxx = -1
            miny = 10000
            maxy = -1
            for j in i:
                if betterCircles[j][0] < minx:
                    minx = betterCircles[j][0] - betterCircles[j][2]
                if betterCircles[j][0] > maxx:
                    maxx = betterCircles[j][0] + betterCircles[j][2]
                if betterCircles[j][1] < miny:
                    miny = betterCircles[j][1] - betterCircles[j][2]
                if betterCircles[j][1] > maxy:
                    maxy = betterCircles[j][1] + betterCircles[j][2]
            #cv.rectangle(src, (minx, miny), (maxx, maxy), (255, 128, 0), 10)
            #cv.putText(src, "Kostka: " + str(len(i)), (minx, miny), cv.FONT_HERSHEY_PLAIN, 4, (255, 255, 0), 10)


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