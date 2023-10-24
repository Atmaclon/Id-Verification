from flask import *
import sqlite3 as sqlite
from script import Camera
from pyzbar.pyzbar import decode
import numpy as np
import cv2
import face_recognition
import math
import io
import base64

app=Flask(__name__)

hostip="192.168.161.153"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def signup():
    return render_template('signup.html')

def face_confidence(face_distance,face_match_threshold=0.6):
    range = (1 - face_match_threshold)
    linear_val= (1.0 -face_distance) / (range * 2)

    if(face_distance>face_match_threshold):
        return str(round(linear_val*100,2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val -0.5)*2,0.2)))*100
        return str(round(value,2)) + '%'

def check(myData,image,face_locations):
    
    num_faces = len(face_locations)
    connection=sqlite.connect("database.db")
    cursor=connection.cursor()
    query="SELECT face_data from users where roll='"+myData+"'"
    cursor.execute(query)
    result=cursor.fetchone()

    if result is None: # User not found in database
       return False
    
    encoding_bytes=result[0]
    act_encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
    connection.close()

    if(num_faces>1):
        return "Error: multiple faces found... Retry again"
    
    face_encodings = face_recognition.face_encodings(image)
    matches = face_recognition.compare_faces(act_encoding, face_encodings, tolerance=0.5)

    if matches[0]== True:
        return True
    else:
        return False
    # matches = face_recognition.compare_faces(act_encoding, face_encodings, tolerance=0.5)
    # if matches[0]== True:
        
    #     return "Face detected and verified. You can move on!!!!!"
    # else:
    #     return "Invalid user face please restart the login process."

@app.route('/validateReg',methods=['POST'])
def validateReg():
    connection=sqlite.connect("database.db")
    cursor=connection.cursor()
    roll =request.form['roll']
    name =request.form['name']
    branch =request.form['branch']
    image = request.files.get("captured_image").read()
    print(roll)
    # print(image)
    #image = base64.b64decode(image)
    image = io.BytesIO(image)
    image = face_recognition.load_image_file(image)

    face_encodings = face_recognition.face_encodings(image)
    face_locations = face_recognition.face_locations(image)

    num_faces = len(face_locations)
    if(num_faces>1):
        connection.commit()
        connection.close()
        return "Error: multiple faces found"
    encoding_bytes = np.array(face_encodings).tobytes()
    
    print(encoding_bytes)

    query="INSERT INTO users (roll, name, branch) VALUES('"+roll+"','"+name+"','"+branch+"')"
    cursor.execute(query)
    connection.commit()

    connection.execute("UPDATE users SET face_data = ?",(encoding_bytes,))
    
    connection.commit()
    connection.close()
    return "Registered User!...."

def gen(camera):
    while True:
        frame = camera.get_frame()
        img= frame

        faceShown=False
        idShown=False


        for code in decode(frame):
            myData= code.data.decode('utf-8')
            print(myData)
            pts=np.array([code.polygon],np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(img,[pts],True,(255,0,255),5)
            idShown=True


        face_locations = face_recognition.face_locations(img)

        if(len(face_locations)==1):
                faceShown=True
        
        if(idShown and faceShown):
            if(check(myData,img,face_locations)):
                cv2.putText(img,"Verified!!!!",(6,26),cv2.QT_FONT_BLACK,0.8,(255,255,255),1)
            else:
                cv2.putText(img,"Your identity does not match our database!!!",(6,26),cv2.QT_FONT_BLACK,0.8,(255,255,255),1)
        elif(idShown):
            cv2.putText(img,"Face Not detected",(6,26),cv2.QT_FONT_BLACK,0.8,(255,255,255),1)
        elif(faceShown):
            cv2.putText(img,"Show Id Please",(6,26),cv2.QT_FONT_BLACK,0.8,(255,255,255),1)
        
        for (top,right,bottom,left) in face_locations:
            cv2.rectangle(img,(left,top),(right,bottom),(0,0,255),2)
            #pnts=np.array([top,right,bottom,left],np.int32)
            #pnts = pnts.reshape((-1,1,2))
            #cv2.polylines(img,pnts,True,(255,0,255),5)
            cv2.putText(img,"Face",(left+6,bottom-6),cv2.FONT_HERSHEY_DUPLEX,0.8,(255,255,255),3)


        sucess,jpeg=cv2.imencode('.jpg',img)

        yield(b'--frame\r\n Content-type:image/jpeg\r\n\r\n'+ jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),mimetype='multipart/x-mixed-replace;boundary=frame')

if __name__ == '__main__':
    app.run(host=hostip,debug =True)
    #app.run(host=hostip,debug =True, ssl_context=('server.crt', 'server.key'))
    