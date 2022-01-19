from mtcnn import MTCNN
from pprint import pprint
import cv2
import pickle
import base64
import numpy as np


def isitgood(person):
    global color
    bad_persons = ['chris-hemsworth']
    if person in bad_persons:
        color = (0,0,255)
        return False
    else :
        color = (255,255,255)
        return True

def process(contents):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    jpg_as_np = np.frombuffer(decoded, dtype=np.uint8)
    image = cv2.imdecode(jpg_as_np, flags=1)
    
    names = list()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    detector = MTCNN()
    faces = detector.detect_faces(image)

    # load the pre-trained model - (recognizer)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainner.yml")

    #load the labels
    labels = dict()
    with open("labels.pickle","rb") as f:
        labels = pickle.load(f)
        labels = {v:k for k,v in labels.items()}

    for box in faces:
        x,y,width,height = box['box']
        x2,y2 = x + width, y + height
        region_of_interest = gray[y:y+y2,x:x+x2]
        id_,conf = recognizer.predict(region_of_interest)
        print(id_,labels[id_],conf)
        font = cv2.FONT_HERSHEY_SIMPLEX

        names.append((labels[id_],conf,str(isitgood(labels[id_]))))
        
        name = str(labels[id_])+"-"+str(round(conf))
        stroke = 1
        cv2.putText(image,name,(x,y),font,0.5,(255,255,255),stroke)
        cv2.rectangle(image,(x,y),(x2,y2),color,stroke)

    cv2.imwrite('temp.png', image)
    return names
