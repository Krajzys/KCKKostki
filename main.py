from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import math

# Function to detect 1
# We check if there are any dots nearby if there aren't
# then it has to be 1
# NOTE: if there is another dice nearby it is possible that we dont find the 1
# Example easy16.jpg
def detect1(circle, circleList): # dziala dla wszystkich poza easy16
    for i in circleList:
        if i[0] != circle[0] and i[1] != circle[1]:
            if distCircle(circle, i) < circle[2]*7.6:
                return False
    return True


# Function to detect 3
# We find nearby dots and then check if there is a dot oposite from the first one
# if so then it is a 3
def detect3(circle, circleList, radius = 4.3):
    #print("3--------------------")
    for i in range(len(circleList)):
        if circleList[i][0] != circle[0] and circleList[i][1] != circle[1]:
            if distCircle(circle, circleList[i]) < circle[2]*radius:
                xdif = circle[0] + (circle[0] - circleList[i][0])
                ydif = circle[1] + (circle[1] - circleList[i][1])
                for j in range(len(circleList)):
                    #print("Mamy:", distCircle((xdif, ydif), circleList[j]))
                    if distCircle((xdif, ydif), circleList[j]) < 40:
                        return (i, j)
    return ()


# Function to detect 5
# We find a 3 and then check if there is another 3 that can be detected3
# Using the same dot as the center if yes then it has to be 5
def detect5(circle, circleList):
    #print("5--------------------")
    detected3 = False
    ret = []
    for i in range(len(circleList)):
        if circleList[i][0] != circle[0] and circleList[i][1] != circle[1]:
            if distCircle(circle, circleList[i]) < circle[2]*4:
                xdif = circle[0] + (circle[0] - circleList[i][0])
                ydif = circle[1] + (circle[1] - circleList[i][1])
                for j in range(len(circleList)):
                    #print("Mamy:", distCircle((xdif, ydif), circleList[j]))
                    if distCircle((xdif, ydif), circleList[j]) < 40:
                        ret.append(i)
                        ret.append(j)
                        detected3 = True
                        break
        if detected3:
            break


    for i in range(len(circleList)):
        if circleList[i][0] != circle[0] and circleList[i][1] != circle[1] and i not in ret and detected3:
            if distCircle(circle, circleList[i]) < circle[2]*4:
                xdif = circle[0] + (circle[0] - circleList[i][0])
                ydif = circle[1] + (circle[1] - circleList[i][1])
                for j in range(len(circleList)):
                    #print("Mamy:", distCircle((xdif, ydif), circleList[j]))
                    if distCircle((xdif, ydif), circleList[j]) < 40:
                        ret.append(i)
                        ret.append(j)
                        return ret
    return ()


# Function to detect 6
# We detect three dots and search for another three dots close by
def detect6(circle, circleList):
    det3 = detect3(circle, circleList, 4)
    if det3:
        for i in range(len(circleList)):
            if circle[0] != circleList[i][0] and circle[1] != circleList[i][1] and distCircle(circle, circleList[i]) < circle[2]*6:
                if i not in det3:
                    det3again = detect3(circleList[i], circleList, 4)
                    if det3again:
                        last = det3 + det3again

                        return tuple([u for u in last] + [i])
    return ()


# Function to detect 4
# We detect close by dot, then we detect another one that
# is 90 degrees in other direction. If we find those two dots
# we calculate middle point between them. Finally we check if there
# is a dot on the oposite side of the middle point.
def detect4(circle, circleList):
    saved = []
    imgPoint = []
    for i in range(len(circleList)):
        if circleList[i][0] != circle[0] and circleList[i][1] != circle[1]:
            if distCircle(circle, circleList[i]) < circle[2]*7:
                #print("4HERE")
                xdifTemp = (circle[0] - circleList[i][0])
                ydifTemp = (circle[1] - circleList[i][1])
                for j in range(len(circleList)):
                    if distCircle((circle[0] + ydifTemp, circle[1] - xdifTemp), circleList[j]) < 40:
                        #print("2HERE")
                        saved.append(i)
                        saved.append(j)
                        break
                    if distCircle((circle[0] - ydifTemp, circle[1] + xdifTemp), circleList[j]) < 40:
                        #print("3HERE")
                        saved.append(i)
                        saved.append(j)
                        break
                if len(saved) == 2:
                    imgPoint.append(int((circleList[saved[0]][0] + circleList[saved[1]][0])/2))
                    imgPoint.append(int((circleList[saved[0]][1] + circleList[saved[1]][1])/2))
                    #print("POINT")
                    #print(circleList[i])
                    #print(imgPoint)
                    #print(circleList[j])
                    #print("Middle:", int((circleList[saved[0]][0] + circleList[saved[1]][0])/2), int((circleList[saved[0]][1] + circleList[saved[1]][1])/2))
                    break

    if len(imgPoint) == 2:
        #return saved
        xpoint = circle[0] - imgPoint[0]
        ypoint = circle[1] - imgPoint[1]
        for i in range(len(circleList)):
            if circleList[i][0] != circle[0] and circleList[i][1] != circle[1]:
                if distCircle((imgPoint[0] - xpoint, imgPoint[1] - ypoint), circleList[i]) < 40:
                    return saved + [i]
                    #print("Lolo")

    return ()


# Function to detect 2
# We only check if there is a close by dot if there is it may be 2
def detect2(circle, circleList):
    for i in range(len(circleList)):
        if circleList[i][0] != circle[0] and circleList[i][1] != circle[1]:
            if distCircle(circle, circleList[i]) < circle[2]*7:
                return [i]
    return ()


# Function to calculate distance between two points
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
    diceEyes = []

    # Trying to find the biggest circle
    maxArea = 0
    for cnt in contours:
        approx = cv.approxPolyDP(cnt, .03 * cv.arcLength(cnt, True), True)
        if len(approx) >= 7:
            area = cv.contourArea(cnt)
            (cx, cy), radius = cv.minEnclosingCircle(cnt)
            circleArea = radius * radius * np.pi
            if abs(circleArea - area) < 2/5*area and area > maxArea:
                maxArea = area

    # Filtering contours to only circular and only big enough
    for cnt in contours:
        approx = cv.approxPolyDP(cnt, .03 * cv.arcLength(cnt, True), True)
        points = [(val[0][0], val[0][1]) for val in cnt]
        if len(approx) >= 7:
            area = cv.contourArea(cnt)
            (cx, cy), radius = cv.minEnclosingCircle(cnt)
            circleArea = radius * radius * np.pi
            if abs(circleArea - area) < 2/5*area and area > maxArea/3:
                cv.drawContours(src, [cnt], 0, (220, 152, 91), -1)
                diceEyes.append((int(cx), int(cy), int(radius)))


    # drawing red outlines around dots
    for i in diceEyes:
        cv.circle(src, (i[0], i[1]), i[2], (0, 0, 255), 7)

    # Grouping dots
    classified = []

    # Search for dices with 1,5,6 dots
    # Only seach for not yet classified dots
    for i in range(len(diceEyes)):
        circ1 = diceEyes[i]
        if detect1(circ1, diceEyes) and i not in classified:
            classified.append(i)
            cv.putText(src, "Kostka 1", (circ1[0], circ1[1]), cv.FONT_HERSHEY_PLAIN, 5.0, (0, 255, 255), 10)
        det5 = detect5(circ1, diceEyes)
        if det5 and i not in classified and det5[0] not in classified and det5[1] not in classified and det5[2] not in classified and det5[3] not in classified:
            classified.append(i)
            for j in det5:
                classified.append(j)
            cv.putText(src, "Kostka 5", (circ1[0], circ1[1]), cv.FONT_HERSHEY_PLAIN, 5.0, (255, 0, 255), 10)
        det6 = detect6(circ1, diceEyes)
        if det6 and i not in classified and det6[0] not in classified and det6[1] not in classified and det6[2] not in classified and det6[3] not in classified and det6[4] not in classified:
            classified.append(i)
            thisSide = list(det6) + [i]
            x = int(np.mean([diceEyes[k][0] for k in thisSide]))
            y = int(np.mean([diceEyes[k][1] for k in thisSide]))
            for j in det6:
                classified.append(j)
            cv.putText(src, "Kostka 6", (x, y), cv.FONT_HERSHEY_PLAIN, 5.0, (0, 120, 255), 10)
            #cv.putText(src, "Kostka 6", (circ1[0], circ1[1]), cv.FONT_HERSHEY_PLAIN, 5.0, (0, 120, 255), 10)

    # Search for dices with 3 dots
    for i in range(len(diceEyes)):
        circ1 = diceEyes[i]
        det3 = detect3(circ1, diceEyes)
        if det3 and i not in classified and det3[0] not in classified and det3[1] not in classified:
            classified.append(i)
            classified.append(det3[0])
            classified.append(det3[1])
            cv.putText(src, "Kostka 3", (circ1[0], circ1[1]), cv.FONT_HERSHEY_PLAIN, 5.0, (255, 255, 0), 10)

    # Search for dices with 4 dots
    for i in range(len(diceEyes)):
        circ1 = diceEyes[i]
        det4 = detect4(circ1, diceEyes)
        #print(det4, classified)
        if det4 and i not in classified and det4[0] not in classified and det4[1] not in classified and det4[2] not in classified:
            classified.append(i)
            classified.append(det4[0])
            classified.append(det4[1])
            classified.append(det4[2])
            thisSide = det4 + [i]
            x = int(np.mean([diceEyes[k][0] for k in thisSide]))
            y = int(np.mean([diceEyes[k][1] for k in thisSide]))
            cv.putText(src, "Kostka 4", (x, y), cv.FONT_HERSHEY_PLAIN, 5.0, (120, 255, 0), 10)

    # Search for dices with to dots
    for i in range(len(diceEyes)):
        circ1 = diceEyes[i]
        det2 = detect2(circ1, diceEyes)
        if det2 and i not in classified and det2[0] not in classified:
            classified.append(i)
            classified.append(det2[0])
            thisSide = det2 + [i]
            x = int(np.mean([diceEyes[k][0] for k in thisSide]))
            y = int(np.mean([diceEyes[k][1] for k in thisSide]))
            cv.putText(src, "Kostka 2", (x, y), cv.FONT_HERSHEY_PLAIN, 5.0, (120, 0, 255), 10)

    # If there are unclassified dots classify them as ones
    for i in range(len(diceEyes)):
        circ1 = diceEyes[i]
        if i not in classified:
            classified.append(i)
            cv.putText(src, "Kostka 1", (circ1[0], circ1[1]), cv.FONT_HERSHEY_PLAIN, 5.0, (0, 255, 255), 10)

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
