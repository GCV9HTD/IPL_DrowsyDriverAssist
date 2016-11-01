import cv2
import numpy as np
import cv2
import time
from datetime import datetime
import requests
import urllib
import urllib2
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import subprocess
import requests
import subprocess
from SOAPpy import SOAPProxy
import glob
import base64
import os
import suds


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 25)

eye_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

#eye close
last_eye_close_timestamp = datetime.now()
firstEyeClose = True
resteEyeCloseCount = False
eyeCloseThreashold = 2.0


#Sound variables
speak = False


while (True):
    ret, img = cap.read()
    img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    # Our operations on the frame come here
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 4, cv2.CASCADE_SCALE_IMAGE, (20, 20))

    #for (x, y, w, h) in faces:
    if len(faces) > 0:
        if(speak == False):
            subprocess.call(['espeak', '-v%s+%s' % ('en', 'f3'), 'Hello. Driver Detected. Device is ready to use'])
            speak = True

        print "Face detected"
        
        #cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        #roi_gray = gray[y:y + (3*h/4), x:x + w]
        eyes = eye_cascade.detectMultiScale(gray,1.3,4,cv2.CASCADE_SCALE_IMAGE,(20,20))

        if len(eyes) == 0:               

            if firstEyeClose == True:
                last_eye_close_timestamp = datetime.now()
                
            timeElapsed = (datetime.now() - last_eye_close_timestamp).seconds
            print "eye closed for " + `timeElapsed`        

            if (firstEyeClose == False and timeElapsed > eyeCloseThreashold):                
                last_eye_close_timestamp = datetime.now()
                firstEyeClose = True
                pygame.mixer.init()
                pygame.mixer.music.load('/home/pi/drowsyCode/beep1.wav')
                pygame.mixer.music.play()
            else:
                firstEyeClose = False
        else:                
            #print "eye opened"
            last_eye_close_timestamp = datetime.now()
            firstEyeClose = True
            timeElapsed = 0
 
    else:
        last_eye_close_timestamp = datetime.now()
        firstEyeClose = True
        timeElapsed = 0    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
