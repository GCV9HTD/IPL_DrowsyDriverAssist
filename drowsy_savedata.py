from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import numpy as np
import cv2
import time
import datetime
import requests
import urllib
import urllib2
import sys
import subprocess


file = open('/home/pi/drowsyCode/not_sleepy.csv','w')
file.write("Blink_Ratio,Blink_Length\n")
# from matplotlib import pyplot as plt


def getRate(timeArray):
    now = time.clock()
    only_past_minute = [x for x in timeArray if x > (now-60)]
    print (only_past_minute)
    
    return len(only_past_minute)

def getThreshold(yawn_frequency,blinkRatio,blink_length_avg):

    # here goes the machine learning / statistical regression model
    # that determines if you're sleepy or not

    print ("Blink_frequency",blinkRatio)
    if (blinkRatio>15):
        return 3
    return 1

camera = PiCamera()
#cap = cv2.VideoCapture(0)

eyes = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_eye.xml")
face_cascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_frontalface_default.xml")
mouth_cascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_mcs_mouth.xml")

# blinking vars
blink_flag = False
blink_bool = False
blink_count = 0
blink_start = 0
blink_frequency = 0.0
eyes_flag2 = 0


# yawning vars
yawn_flag = False
yawn_flag2 = 0
yawn_bool = False
yawn_count = 0
yawn_frequency = 0.0
yawn_start = 0

width=500
height=500
camera.resolution=(width,height)
camera.framerate = 25
time.sleep(2)
##camera.shutter_speed =  camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
camera.iso = 400
rawCapture = PiRGBArray(camera, size=(width,height))

rawCapture.truncate(0)

overallTime = time.clock()
timeToSend = time.clock()
sent = False
recorded_time_blink=False

blinkArr = []
blinkLengthArr = []
longestBlink = 0
blink_length_avg = -1
lastBlink = time.clock() #set to start at 0

yawnTimes = []
txt = ""
blinkRatio = 0
tmpSaving=False

subprocess.call(['espeak', '-v%s+%s' % ('en', 'f3'), 'Hello. Your Device is setup and Ready to use'])
faceDetected = True
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    #ret, img = cap.read()
    #img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    img = frame.array
    # Our operations on the frame come here
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # faces = face_cascade.detectMultiScale(gray, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20))

    blink_flag = False

    #frame = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)

    # print frame.shape

    faces = face_cascade.detectMultiScale(gray, 1.3, 5, cv2.CASCADE_SCALE_IMAGE, minSize=(20, 20))
    x=0
    y=0
    w=0
    h=0
    for (x, y, w, h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
##        if faceDetected == True:
##            subprocess.call(['espeak', '-v%s+%s' % ('en', 'f3'), 'Driver Detected'])
##            faceDetected = False
        #eye_frame = gray[(y+h/5):(y+h/2), x:x+w]           # take a zorro mask subset
        eye_frame = gray[y:y+h, x:x+w]
        eye_frame_color = img[y:y+h, x:x+w]
        #cv2.imshow("Faces",faces)

        detected = eyes.detectMultiScale(eye_frame)
        ex=0
        ey=0
        ew=0
        eh=0
        for(ex,ey,ew,eh) in detected:
            cv2.rectangle(eye_frame_color, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)
        if len(detected) == 0:
            if eyes_flag2 > 0:
                blink_flag = True
                eyes_flag2 = 0
            else:
                eyes_flag2 += 1
        else:
            eyes_flag2 = 0
            if blink_bool and recorded_time_blink == False:
                # opened eyes, so record the time they were closed
                timeSpent = (time.clock() - blink_start)
                print "Time Spent" , timeSpent
                if timeSpent > longestBlink:
                    longestBlink = timeSpent
                    
                print ("Blink was:",timeSpent," seconds long")

                if len(blinkLengthArr) < 10:
                    blinkLengthArr.append(timeSpent)

                else:
                    blinkLengthArr = blinkLengthArr[1:]
                    blinkLengthArr.append(timeSpent)
                recorded_time_blink = True

                # display average blinking time
                last_minute_blinking = blinkLengthArr
                print (last_minute_blinking)
                blink_length_avg = -1

                if not(last_minute_blinking == []):
                    blink_length_avg = sum(last_minute_blinking)/(float(len(last_minute_blinking)))
                    print ("Average blinking time is ", blink_length_avg)
            blink_flag = False

        #cv2.imshow("eyes",eye_frame)

        #roi_gray_mouth = gray[(y+h/2):(y+(8*h/9)), (x+w/5):(x +4*w/5)]
        roi_gray_mouth = gray[(y+h/2):y+h, x:x + w]
        roi_color_mouth = img[(y+h/2):y+h, x:x + w]
        #cv2.imshow("mouth", roi_gray_mouth)

        mouth = mouth_cascade.detectMultiScale(roi_gray_mouth) #,1.3, 4, cv2.CASCADE_SCALE_IMAGE, (20, 20))
        # print "Length:",len(mouth)
        mx=0
        my=0
        mw=0
        mh=0
        for (mx, my, mw, mh) in mouth:
            # print "finding mouth"
            mouth_detected = True
            cv2.rectangle(roi_color_mouth, (mx, my), (mx + mw, my + mh), (255, 0, 255), 2)
            #roi_gray_mouth = gray[my:my+mh*2, mx:mx + 2*mw]
           
            if mouth_detected:
                break

        if len(mouth) == 0:
            if yawn_flag2 > 3:
                yawn_flag = True
                yawn_flag2 = 0
            else:
                yawn_flag2 += 1
        else:
            yawn_flag = False
            yawn_flag2 = 0

        break

    
    cv2.imshow("PiCam", gray)
    
    if (time.clock() - blink_start) > 1:
        if (blink_flag == False):
            blink_bool = False
            recorded_time_blink = False

    if (time.clock() - yawn_start) > 5.0:
        if yawn_flag == False:
            yawn_bool = False

        # now, if flag is true, then figure out blinking
    if (blink_flag == True):
        if (blink_bool == False):
            # start timer
            blink_start = time.clock()
            blink_bool = True
            blink_count += 1

            #time - lastBlink = time since last blink
            if (len(blinkArr)<50):
                blinkArr.append(time.clock())
            else:
                blinkArr = blinkArr[1:]
                blinkArr.append(time.clock())
            # print "Blink Array: ",blinkArr
            blinkRatio = getRate(blinkArr)
            print ("Blink Ratio: ",blinkRatio, "blinks per minute")

        # else:
        #     print "detect blink but disabled"
        # get the time spent

    if yawn_flag:
        # print "Yawn Flag:", yawn_flag, "Yawn Bool: ", yawn_bool
        if not yawn_bool:
            yawn_start = time.clock()
            yawn_bool = True
            yawn_count += 1
            print ("Detect yawn, total:", yawn_count)
            print ("Yawn Frequency: ", yawn_frequency, " in ", (time.clock() - overallTime), " sec")


        # if less than 20 ms, do nothing
    timeElapsed = int(time.clock() - timeToSend)
##    print "BlinkLengthAvg:",blink_length_avg,"YawnnCount",yawnCount,
##    if (timeElapsed>0 and (timeElapsed%30==0) and sent==False):
    if (yawn_frequency > 10 or blink_length_avg > 3 or longestBlink >5 or blinkRatio >4): #Assume Drowsy
        if(tmpSaving==False):
            tmp = img
            tmpSaving=True
        drowsyTime = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        print ("\n\n\n\n ----- SAVING DATA ------- \n")
        # CALCULATE THRESHOLD
        #blink_length_avg = 1
        threshold = getThreshold(yawn_frequency,blinkRatio,blink_length_avg)

        print ("STEP 1: Raise Alarm \n")
        pygame.mixer.init()
        pygame.mixer.music.load('/home/pi/drowsyCode/raid.wav')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
           continue
        
        print ("STEP 2: Save the image")
        fileName = "/home/pi/drowsyImages/"+drowsyTime +".jpg"
        cv2.imwrite(fileName, tmp)
        tmpSaving=False

        print ("STEP 3: Invoke Web Service\n")
        #payload = {'yawnRate':yawn_frequency , 'blinkRate':blinkRatio, 'blinkLength':blink_length_avg, 'threshold':threshold }
        url = "<<SOAP URL GOES HERE>>"
        headers = {'content-type': 'text/xml'}
        body = """<?xml version="1.0" encoding="UTF-8"?>
         <SOAP-ENV:Envelope xmlns:ns0="http://ws.cdyne.com/WeatherWS/" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
            <SOAP-ENV:Header/>
              <ns1:Body><ns0:GetWeatherInformation/></ns1:Body>
         </SOAP-ENV:Envelope>"""
        with open(fileName, "rb") as imageFile:
            f= imageFile.read()
            b= bytearray(f)
        #r = requests.post(url,data=body,headers=headers)
        
        txt = str(blinkRatio)+','+str(blink_length_avg)+'\n'
        file.write(txt)
        yawn_frequency = 0
        blink_length_avg = -1
        longestBlink = 0
        blinkRatio = 0
##        sent = True
##    if (timeElapsed%30==1):
##        sent = False

    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)

    if key==ord("q"):
        break  # time.sleep(1)

print ("WRITING DATA")

file.write(txt)
file.close()
# When everything done, release the capture
# cap.release()
cv2.destroyAllWindows()
