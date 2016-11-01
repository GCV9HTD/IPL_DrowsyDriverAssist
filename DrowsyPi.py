from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

camera = PiCamera()


eye_cascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_eye.xml")
face_cascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_frontalface_alt.xml")
mouth_cascade = cv2.CascadeClassifier("/home/pi/drowsyCode/haarcascade_mcs_mouth.xml")

blinkBool = False
blinkCount = 0
blinkFlag = False
blinkStart = 0
blinkFrequency = 0.0
eyesFlag2 = 0
blinkDuration = 3.0

yawnFlag = False
yawnFlag2 = 0
yawnBool = False
yawnCount = 0
yawnFrequency =0.0
yawnStart = 0
yawnDuration = 4.0

recorded_time_blink=False

start = 0
width=500
height=500

camera.resolution=(width,height)
camera.framerate = 30
time.sleep(2)
camera.shutter_speed =  camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
camera.iso = 200
rawCapture = PiRGBArray(camera, size=(width,height))

rawCapture.truncate(0)

startTime = time.clock()
sendTime = time.clock()
sent = False
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    #grab the frame
    image = frame.array
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #show the frame
   

    faces = face_cascade.detectMultiScale(gray, 1.3, 4, cv2.CASCADE_SCALE_IMAGE, (50,50))
    blinkFlag = False
    print "Detected ",len(faces)," faces"
    fx=0
    fy=0
    fw=0
    fh=0
    for (x,y,w,h) in faces:
        drowsyEye = False
        yawningMouth = False
        cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[(y+h/5):(y+h/2), x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray, minNeighbors=4, scaleFactor=1.05, minSize=(5, 5))
        eyesDetected = 0
        for (ex,ey,ew,eh) in eyes:
            eyesDetected +=1
            cv2.rectangle(roi_gray,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
            print "Detected ",len(eyes),"eyes"
            #cv2.imshow("Frame",gray)
            if(eyesDetected >=2):
                break
        if len(eyes) == 0:
            if eyesFlag2 > 0:
                blinkFlag =True
                eyesFlag2 = 0
            else:
                eyesFlag2 +=1
        else:
            blinkFlag = False
            eyesFlag2 = 0
            if blinkBool and recorded_time_blink == False:
                # opened eyes, so record the time they were closed
                timeSpent = (time.clock() - blinkStart)
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

        roi_gray_mouth = gray[(y+h/2):(y+(8*h/9)), (x+w/5):(x +4*w/5)]
        roi_color_mouth = image[(y+h/2):y+h, x:x + w]
        mouth = mouth_cascade.detectMultiScale(roi_gray_mouth,1.05, 4, cv2.CASCADE_SCALE_IMAGE, (10, 10))
        for (mx, my, mw, mh) in mouth:
            mouthDetected = True
            cv2.rectangle(roi_color_mouth, (mx, my), (mx + mw, my + mh), (255, 0, 255), 2)
            roi_gray_mouth = gray[my:my+mh*2, mx:mx + 2*mw]
            print "Detected ", len(mouth), "mouth"
            if mouthDetected:
                break

        if len(mouth) == 0:
            if yawnFlag2 > 5:
                yawnFlag = True
                yawnFlag2 = 0
            else:
                yawnFlag2 +=1
        else:
            yawnFlag = False
            yawnFlag2 = 0

        #Reached Outside
        if(time.clock() - blinkStart) > blinkDuration:
            print "Eyes Closed more than ", blinkDuration, " No of eyes", len(eyes)
            if(blinkFlag == False):
                blinkBool = False
            if(len(eyes)> 0): #partial success
                drowsyEye = True
                
        if(time.clock() - yawnStart) > yawnDuration:
            print "Yawning more than ", yawnDuration, "No of mouth", len(mouth)
            if yawnFlag == False:
                yawnBool = False
            if(len(mouth) > 0):
                yawningMouth = True
                

        #If flag is set, calc blinking
        if(blinkFlag == True):
            if(blinkBool == False):
                blinkStart = time.clock()
                blinkBool = True
                blinkCount +=1
                print "Blink detected Total: ", blinkCount

        if(yawnFlag == True):
            if(yawnBool == False):
                yawnStart = time.clock()
                yawnBool = True
                yawnCount +=1
                print "Yawn detected Total: ", yawnCount

        #if less than 20 ms, do thing
        timeElapsed = int(time.clock() - sendTime)
        print "time elapsed ", timeElapsed
##        if(timeElapsed > 0 and (timeElapsed%20==0) and sent == False):
##            fileName = "/home/pi/drowsyImages/", time.clock(),".jpeg"
##            cv2.imwrite(fileName, image)
##            sent = True
            
##        if(timeElapsed%20==1):
##            sent = False
        if(drowsyEye or yawningMouth):
            print "WAKE UP DUMMY"
            drowsyEye = False
            yawningMouth = False


    
    cv2.imshow("Frame",gray)
        
    
    
    key = cv2.waitKey(1)&0xFF
    #clear stream
    rawCapture.truncate(0)
    #quit on 'q'
    if key==ord("q"):
        break
    
