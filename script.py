import cv2
import numpy as np
#from pyzbar.pyzbar import decode

class Camera(object):
    def __init__(self):
        #self.img=cv2.imread('1.png')
        self.cap =cv2.VideoCapture(0)
    
    def __del__(self):
        self.cap.release()

    def get_frame(self):
        
        success,img= self.cap.read()
        #qrcode = decode(img)
        #sucess,jpeg=cv2.imencode('.jpg',img)
        #cv2.imshow('Result',img)
        #cv2.waitKey(1)
        #return jpeg.tobytes()
        return img