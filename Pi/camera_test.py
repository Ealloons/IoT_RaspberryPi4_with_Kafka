import cv2
import picamera
import time
from kafka import KafkaProducer
from json import dumps
from datetime import datetime
import base64
import json
import numpy as np

producer = KafkaProducer(acks=0, compression_type='gzip', bootstrap_servers=['192.168.35.145:9092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8'))

camera = picamera.PiCamera()


while True:
    time.sleep(100)
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    camera.annotate_text = now
    camera.resolution=(1024,768)
    camera.capture('snapshot.jpg',resize=(500,500))
    img = cv2.imread('./snapshot.jpg')
    image_string = cv2.imencode('.jpg', img)[1]
    image_string = base64.b64encode(image_string).decode()
    print('send image')
    
    image = {
    'm_id' : '0',
    'datetime' : now,
    'photo': image_string
    }
    producer.send('imgtest', value=image)
    producer.flush()