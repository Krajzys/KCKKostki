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
def detect3(circle, circleList):
	#print("3--------------------")
	for i in range(len(circleList)):
		if circleList[i][0] != circle[0] and circleList[i][1] != circle[1]:
			if distCircle(circle, circleList[i]) < circle[2]*4:
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
			
		det3 = detect3(circ1, diceEyes)
		if det3 and i not in classified and det3[0] not in classified and det3[1] not in classified:
			classified.append(i)
			classified.append(det3[0])
			classified.append(det3[1])
			cv.putText(src, "Kostka 3", (circ1[0], circ1[1]), cv.FONT_HERSHEY_PLAIN, 5.0, (255, 255, 0), 10)
		

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