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

# from matplotlib import pyplot as plt
##camera = PiCamera()
##width=500
##height=500
##camera.resolution=(width,height)
##time.sleep(2)
##rawCapture = PiRGBArray(camera, size=(width,height))
##
##rawCapture.truncate(0)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 25)

eye_cascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_eye.xml")
handCascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_hand.xml")
face_cascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_frontalface_default.xml")
mouth_cascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_mcs_mouth.xml")


# Webservice
url="http://drowsyservice.azurewebsites.net/DrowsyService.svc?wsdl"
headers = {'content-type': 'application/soap+xml'}
path ='/home/pi/drowsyImages/*.jpg'
namespace = "http://tempuri.org/"
server = SOAPProxy(url,namespace)
client = suds.client.Client(url)
files = glob.glob(path)


# blinking vars
blink_flag = False
blink_bool = False
blink_count = 0
blink_start = 0
blink_frequency = 0.0
eyes_flag2 = 0
blink_duration = 2.0
first_blink = True
blink_span_threshold = 2.0
last_eye_close_timestamp = time.clock()
last_eye_close_detected = False

# yawning vars
yawn_flag = False
yawn_flag2 = 0
yawn_bool = False
yawn_count = 0
yawn_frequency = 0.0
yawn_start = 0
yawn_duration = 3.0


startTime = time.clock()
timeToSend = time.clock()
sent = False
test1=time.clock()
bool_ec=False
bool_ecf=False
speak = False



def sendWebservice():
    for name in files:
        try:
            encoded_string = ""
            with open(name, "rb") as f:
                encoded_string = base64.b64encode(f.read())
            #b = bytearray(f.read())
            #print b
            
            print name.split("/")[4].replace('.jpg','')
            subprocess.call(["curl", "-X", "POST", "-H", "Content-Type: text/xml", "-H", "SOAPAction: \"http://tempuri.org/IDrowsyService/StoreDrowsyDetails\"",
            "-d", """<?xml version="1.0" encoding="UTF-8"?>
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:drow="http://schemas.datacontract.org/2004/07/DrowsyMonitorService">
                       <soapenv:Header/>
                       <soapenv:Body>
                          <tem:StoreDrowsyDetails>
                          <tem:data>
                               <drow:AlertImage>"""+encoded_string+"""</drow:AlertImage>        
                           </tem:data>
                          </tem:StoreDrowsyDetails>
                       </soapenv:Body>
                    </soapenv:Envelope>""" , "http://drowsyservice.azurewebsites.net/DrowsyService.svc"])

            print "Data sent to Webservice successfully"
            os.rename (name, name+"Proc");
        except Exception as exc:
            print 'Unsuccessful', exc

def saveSate(drowsyTime, tmp):
    run1 = time.clock()
    print ("STEP 1: Raise Alarm \n")
    pygame.mixer.init()
    pygame.mixer.music.load('/home/pi/drowsyCode/beep1.wav')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    #subprocess.call(['espeak', '-v%s+%s' % ('en', 'f3'), 'Sleeping'])

        
    print ("STEP 2: Save the image")
    fileName = "/home/pi/drowsyImages/"+drowsyTime +".jpg"
    #if(time.clock() - run1) > 4.0:
    cv2.imwrite(fileName, tmp)
    tmpSaving=False
 

##    print ("STEP 3: Invoke Web Service\n")
##    #payload = {'yawnRate':yawn_frequency , 'blinkRate':blinkRatio, 'blinkLength':blink_length_avg, 'threshold':threshold }
##    url="http://drowsyservice.azurewebsites.net/DrowsyService.svc?wsdl"
##    headers = {'content-type': 'text/xml'}
##    try:
##        encoded_string = ""
##        with open(name, "rb") as f:
##            encoded_string = base64.b64encode(f.read())
##        body = """<?xml version="1.0" encoding="UTF-8"?>
##                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:drow="http://schemas.datacontract.org/2004/07/DrowsyMonitorService">
##                       <soapenv:Header/>
##                       <soapenv:Body>
##                          <tem:StoreDrowsyDetails>
##                             <tem:data>
##                                <drow:AlertImage>"""+encoded_string+"""</drow:AlertImage>       
##                                <drow:AlertTime>"""+name.split('/')[4]+ """</drow:AlertTime>
##                             </tem:data>
##                          </tem:StoreDrowsyDetails>
##                       </soapenv:Body>
##                    </soapenv:Envelope>"""
##        response = requests.post(url,data=body,headers=headers)
##        print "Success"
##     except Exception as exc:
##        print 'Unsuccessful', exc
    
while(True):
#for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    ret, img = cap.read()
    #img = frame.array
    blink_frequency = 60 * blink_count / ((time.clock() - startTime))
    yawn_frequency = 60 * yawn_count / ((time.clock() - startTime))

    # while(True):
    # Capture frame-by-frame
    # ret, img = cap.read()
    # img = cv2.imread('family.jpg')
    img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    # Our operations on the frame come here
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 4, cv2.CASCADE_SCALE_IMAGE, (30, 30))

    blink_flag = False

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + (3*h/4), x:x + w]
        roi_color = img[y:y + (3*h/4), x:x + w]
        if(speak == False):
            subprocess.call(['espeak', '-v%s+%s' % ('en', 'f3'), 'Hello. Driver Detected. Device is ready to use'])
            speak = True
        eyes = eye_cascade.detectMultiScale(roi_gray,1.3,4,cv2.CASCADE_SCALE_IMAGE,(10,10))
        eyes_detected = 0
        for (ex, ey, ew, eh) in eyes:
            eyes_detected += 1
            eye_img = roi_gray[ey:ey+eh, ex:ex+ew]
            eye_img_color = roi_color[ey:ey+eh, ex:ex+ew]
            # cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            # # hist = cv2.calcHist(eye_img,[0],None,[256],[0,256])
            # circles = cv2.HoughCircles(eye_img,cv2.HOUGH_GRADIENT,1,120,
            #                 param1=50,param2=30,minRadius=5,maxRadius=30)
            # # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 75)
            # if circles is not None:
            #     # print len(circles) ,"circles found on 1 eye"
            # # convert the (x, y) coordinates and radius of the circles to integers
            #     circles = np.round(circles[0, :]).astype("int")

            #     # loop over the (x, y) coordinates and radius of the circles
            #     for (x, y, r) in circles:
            #         # draw the circle in the output image, then draw a rectangle
            #         # corresponding to the center of the circle
            #         cv2.circle(eye_img_color, (x, y), r, (0, 0, 255), 4)
            #         # cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            if (eyes_detected==2):
                break
       
        if len(eyes) ==0:
            #print "In if : ", len(eyes)
            # print "eyes closed"
            test2=time.clock()
            #print "!!!!!!! ", test2-test1, "bool_ecf ", bool_ecf
            if (bool_ecf==False):
                #print "????????????"
                bool_ecf=True                
                test1=time.clock()
            elif (bool_ecf==True and (test2-test1) > blink_span_threshold) :
                print "Drowsy Driver Detected"
                
                saveSate(datetime.now().strftime("%m_%d_%Y_%H_%M_%S"), img)

                print "STEP 3: Sending data to Webservice \n"
                sendWebservice()
                
                bool_ecf=False
                test1=time.clock()
                break;
            #print "GGGGGGG : ", bool_ecf
            #print last_eye_close_timestamp, "  ", datetime.now()
            #if last_eye_close_detected and (datetime.now() - last_eye_close_timestamp).total_seconds() > blink_span_threshold and first_blink==False:
                #print "Blink duration is more -- Alarm !!! and save"
                       
            if first_blink == True:
                last_eye_close_timestamp = datetime.now()
            
            last_eye_close_detected = True
            first_blink = False 
            
            if eyes_flag2>0:
                blink_flag = True
                eyes_flag2 = 0
            else:
                eyes_flag2+=1
        else:
            #print "In else : ", len(eyes)
            blink_flag = False
            eyes_flag2 = 0
            last_eye_close_detected = False
            first_blink =  True
            bool_ecf=False            
            # limit to 1

        roi_gray_mouth = gray[(y+h/2):y+h, x:x + w]
        roi_color_mouth = img[(y+h/2):y+h, x:x + w]

        mouth = mouth_cascade.detectMultiScale(roi_gray_mouth,1.3, 4, cv2.CASCADE_SCALE_IMAGE, (20, 20))

        for (mx, my, mw, mh) in mouth:
            mouth_detected = True
            cv2.rectangle(roi_color_mouth, (mx, my), (mx + mw, my + mh), (255, 0, 255), 2)
            roi_gray_mouth = gray[my:my+mh*2, mx:mx + 2*mw]
            # circles = cv2.HoughCircles(roi_gray_mouth,cv2.HOUGH_GRADIENT,1,120,
            #         param1=50,param2=20,minRadius=10,maxRadius=300)
            # if circles is not None:
            #     # print len(circles) ,"circles found on 1 mouth"
            # # convert the (x, y) coordinates and radius of the circles to integers
            #     circles = np.round(circles[0, :]).astype("int")

            #     # loop over the (x, y) coordinates and radius of the circles
            #     for (x, y, r) in circles:
            #         # draw the circle in the output image, then draw a rectangle
            #         # corresponding to the center of the circle
            #         cv2.circle(roi_color_mouth, (x, y), r, (0, 0, 255), 4)
                    # cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            if mouth_detected:
                break

        if len(mouth) == 0:
            if yawn_flag2>0:
                yawn_flag = True
                yawn_flag2 = 0
            else:
                yawn_flag2+=1
        else:
            yawn_flag = False
            yawn_flag2 = 0

    
    if (time.clock() - blink_start) > blink_duration:
        if (blink_flag == False):
            blink_bool = False
    
    if (time.clock() - yawn_start) > yawn_duration:
        if yawn_flag == False:
            yawn_bool = False

        # now, if flag is true, then figure out blinking
    if (blink_flag == True):
        if (blink_bool == False):
            # start timer
            blink_start = time.clock()
            blink_bool = True
            blink_count += 1
            #print "Drowsy Driver"
            #print "Detect blink, total:", blink_count
            #print "Blink Frequency: ", blink_frequency, " in ", (time.clock() - startTime), " sec"
##        else:
##            last_blink_detected = False
##    else:
##        last_blink_detected = False

    if yawn_flag:
        # print "Yawn Flag:", yawn_flag, "Yawn Bool: ", yawn_bool
        if not yawn_bool:
            yawn_start = time.clock()
            yawn_bool = True
            yawn_count += 1
            print "Detect yawn, total:", yawn_count
            #print "Yawn Frequency: ", yawn_frequency, " in ", (time.clock() - startTime), " sec"

            # print "detected yawn but disabled"

        # if less than 20 ms, do nothing
    #timeElapsed = int(time.clock() - timeToSend)
    # print "Elapsed time:",timeElapsed
    #if (timeElapsed>0 and (timeElapsed%20==0) and sent==False):
        #print "\n\n\n\n ----- SENDING DATA ------- \n"
        #payload = {'yawnRate':yawn_frequency , 'blinkRate':blink_frequency}
        #url = "https://mhealthhelloworld-bpeynetti.c9users.io/insert.php"
        #r = requests.post(url,data=payload)
        #print r.text
        sent = True
    #if (timeElapsed%20==1):
    #    sent = False
    # if (int(time.clock() - timeToSend)%10)==0:
    #     print "\n\n ------ SENDING DATA --------"
    #     payload = {'yawnRate':yawn_frequency , 'blinkRate':blink_frequency}
    #     url = "https://mhealthhelloworld-bpeynetti.c9users.io/insert.php"
    #     r = requests.post(url,data=payload)
    #     print r.text
    # print "Found ",len(eyes)," eyes!"
    # print "Found ",len(eyes)," eyes!"
    # print "Found ",len(faces)," faces!"
    # Display the resulting frame
    #cv2.imshow('Video', img)
    #if (blink_count == 50):
    #    break
    #rawCapture.truncate(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # time.sleep(1)
# cv2.waitKey(0)    

# When everything done, release the capture
# cap.release()
cv2.destroyAllWindows()
