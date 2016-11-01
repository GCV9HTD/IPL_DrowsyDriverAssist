import cv2
from datetime import datetime

history = numpy.array([],dtype=numpy.int32)
 
class Webcam(object):
 
    WINDOW_NAME = "Driver Surveillance System"
 
    # constructor
    def __init__(self):
        self.webcam = cv2.VideoCapture(0)
         
    # save image to disk
    def _save_image(self, path, image):
        filename = datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '.jpg'
        cv2.imwrite(path + filename, image)
 
    # obtain changes between images
    def _delta(self, t0, t1, t2):
        d1 = cv2.absdiff(t2, t1)
        d2 = cv2.absdiff(t1, t0)
        return cv2.bitwise_and(d1, d2)
 
    # detect faces in webcam
    def detect_faces(self):
 
        # get image from webcam
        img = self.webcam.read()[1]
         
        # do face/eye detection
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
 
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
 
        for (x,y,w,h) in faces:
 
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
 
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
 
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
 
            # save image to disk
            if(len(eyes)== 0):
                self._save_image('/home/beingsuplab/WebCam/Detection/', img)
 
        # show image in window
        cv2.imshow(self.WINDOW_NAME, img)
        cv2.waitKey(1000)
 
        # tidy and quit
        cv2.destroyAllWindows()
 
        if len(faces) == 0:
            return False
 
        return True
 
    # wait until motion is detected 
    def detect_sleep(self):
 
        # set motion threshold
        threshold = 170000
 
        # hold three b/w images at any one time
        t_minus = cv2.cvtColor(self.webcam.read()[1], cv2.COLOR_RGB2GRAY)
        t = cv2.cvtColor(self.webcam.read()[1], cv2.COLOR_RGB2GRAY)
        t_plus = cv2.cvtColor(self.webcam.read()[1], cv2.COLOR_RGB2GRAY)
 
        # now let's loop until we detect some motion
        while True:
   
          # obtain the changes between our three images 
          delta = self._delta(t_minus, t, t_plus)
   
          # display changes in surveillance window
          cv2.imshow(self.WINDOW_NAME, delta)
          cv2.waitKey(10)
 
          # obtain white pixel count i.e. where motion detected
          count = cv2.countNonZero(delta)
 
          # debug
          #print (count)
 
          # if the threshold has been breached, save some snaps to disk
          # and get the hell out of function...
          if (count > threshold):
 
              self._save_image('WebCam/Motion/', delta)
              self._save_image('WebCam/Photograph/', self.webcam.read()[1])
 
              cv2.destroyAllWindows()
              return True
 
          # ...otherise, let's handle a new snap
          t_minus = t
          t = t_plus
          t_plus = cv2.cvtColor(self.webcam.read()[1], cv2.COLOR_RGB2GRAY)



print "Start"
webcam = Webcam()
#webcam.detect_sleep()
while True:
    # get image from webcam
    img = self.webcam.read()[1]
         
    # do face/eye detection
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
 
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
 
    for (x,y,w,h) in faces:
 
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
 
          roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
 
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
 
            # save image to disk
            if(len(eyes)== 0):
                self._save_image('/home/beingsuplab/WebCam/Detection/', img)
 
        # show image in window
        cv2.imshow(self.WINDOW_NAME, img)
        cv2.waitKey(1000)
 
        # tidy and quit
        cv2.destroyAllWindows()

