#!/usr/bin/python
import cv2
import time
from PIL import Image
import os
import numpy as np
import time
import pygame

#----------------------------------------------------------------------------
# Face Detection Test based on OpenCV)
# Modified/using examples from:
# 
# http://japskua.wordpress.com/2010/08/04/detecting-eyes-with-python-opencv
#----------------------------------------------------------------------------

#not needed 
#pygame.init()
#pygame.mixer.init()

def raiseAlarm():
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
                clock.tick(FRAMERATE)

                

FREQ = 44100   # same as audio CD
BITSIZE = -16  # unsigned 16 bit
CHANNELS = 2   # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
FRAMERATE = 1000 # how often to check if playback has finished
pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
soundfile = 'alarm.wav'
clock = pygame.time.Clock()
pygame.mixer.music.load(soundfile)


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_mcs_lefteye.xml')
l_eye = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
r_eye = cv2.CascadeClassifier('haarcascade_righteye_2splits.xml')

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_BRIGHTNESS, 160)
capture.set(cv2.CAP_PROP_EXPOSURE, 20.0)
name = 'detect'

cv2.namedWindow(name, cv2.WINDOW_AUTOSIZE)
ocur=0

Threshold =2

while True:
        
        s, img = capture.read()
        if s <> None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 3) #hmm, 5 required neighbours is actually a lot.
                for (x,y,w,h) in faces:
                        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),1) # if you want colors, don't paint into a grayscale...
##                        face_center = (((x+w)/2.0), ((y+h)/2.0))
##                        face_diameter = h-y
##                        eyeBBox = np.array([x, (y+(face_diameter*0.24)), w, (h- (face_diameter*0.40))], dtype= np.int16);
##
##                        EYE_MIN_SIZE = 0.15
##                        bBoxScaled = eyeBBox * 0.3333
##                        eyes_roi = img[bBoxScaled[1]:bBoxScaled[3], bBoxScaled[0]:bBoxScaled[2]]
##                        print "here"
##                        #eyes_roi = cv2.equalizeHist(eyes_roi, 0)
##                        minEyeSize = eyes_roi.shape[1]*0.15
##                        
##                        print minEyeSize
                        roi_gray = gray[y:y+h, x:x+w]
                        roi_color = img[y:y+h, x:x+w]
##                        eyes = eye_cascade.detectMultiScale(img, minSize=(int(round(minEyeSize)),40), flags=cv2.CASCADE_SCALE_IMAGE )
                        eyes = r_eye.detectMultiScale(roi_gray)
                        for (ex,ey,ew,eh) in eyes:
                                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),1)
                        print len(eyes)
                        if len(eyes) == 0:
                                ocur+=1
                                if ocur==1:
                                        t1=time.time()                  
                        if ocur > 1:
                                t2=time.time()
                                ocur=0
                                print t2-t1
                                if t2-t1 > Threshold: #t2-t1 <2
                                        raiseAlarm()
##                                               
                cv2.imshow(name, img)    

        if cv2.waitKey(1) & 0xFF == ord('q'):
                break

capture.release()
cv2.destroyAllWindows()

