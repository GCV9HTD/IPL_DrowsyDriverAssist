#Identify pupils. Based on beta 1

import numpy as np
import cv2
import time
from datetime import datetime
import os

cap = cv2.VideoCapture(0)   #640,480
w = 640
h = 480
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eyes_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')


#eye close
last_eye_close_timestamp = datetime.now()
firstEyeClose = True
resteEyeCloseCount = False
eyeCloseThreashold = 2
timeElapsed = 0


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:

        #frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        # Our operations on the frame come here
        frame = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(frame, 1.3, 4, cv2.CASCADE_SCALE_IMAGE, (20, 20))
    
        #downsample
        #frameD = cv2.pyrDown(cv2.pyrDown(frame))
        #frameDBW = cv2.cvtColor(frameD,cv2.COLOR_RGB2GRAY)
    
        #detect face
        #frame = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)

        for (x, y, w, h) in faces:
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            #roi_gray = gray[y:y + (3*h/4), x:x + w]
            #roi_color = frame[y:y + (3*h/4), x:x + w]
        
            roi_gray = frame[y:y + (3*h/4), x:x + w]
            eyes_detected = eyes_cascade.detectMultiScale(roi_gray, 1.3, 5)
            #eyes_detected = eye_cascade.detectMultiScale(roi_gray,1.3,4,cv2.CASCADE_SCALE_IMAGE,(20,20))
    
            #faces = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            #detected2 = faces.detectMultiScale(frameDBW, 1.3, 5)
        
            pupilFrame = frame
            pupilO = frame
            windowClose = np.ones((5,5),np.uint8)
            #windowOpen = np.ones((2,2),np.uint8)
            #windowErode = np.ones((2,2),np.uint8)

            if len(eyes_detected) == 0:
                timeElapsed = (datetime.now() - last_eye_close_timestamp).seconds
                
                if (firstEyeClose == False and timeElapsed > eyeCloseThreashold):
                    print "eye closed for " + `timeElapsed`
                
                if firstEyeClose == True:
                    #print last_eye_close_timestamp
                    last_eye_close_timestamp = datetime.now()

                firstEyeClose = False
            else:                
                print "eye opened"
                firstEyeClose = True
                timeElapsed = 0
                

        #show picture        
       # cv2.imshow('frame',frame)
        #cv2.imshow('frame2',pupilFrame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    #else:
        #break

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()
