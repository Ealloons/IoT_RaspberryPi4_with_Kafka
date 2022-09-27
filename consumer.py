from pymongo import MongoClient
from kafka import KafkaConsumer
from json import loads
import os
from multiprocessing import Process
from threading import Thread
from confluent_kafka import Consumer
from datetime import datetime
# topic, broker list
# temp_consumer = KafkaConsumer(
#     'temp_test',
#      bootstrap_servers=['192.168.35.145:9092'],
#      auto_offset_reset='latest',
#      enable_auto_commit=True,
#      group_id='my-group',
#      value_deserializer=lambda x: loads(x.decode('utf-8')),
#      consumer_timeout_ms=1000
# )
# img_consumer = KafkaConsumer(
#     'imgtest',
#      bootstrap_servers=['192.168.35.145:9092'],
#      auto_offset_reset='latest',
#      enable_auto_commit=True,
#      group_id='my-group',
#      value_deserializer=lambda x: loads(x.decode('utf-8')),
#      consumer_timeout_ms=1000
# )
client = MongoClient("mongodb://localhost:27017/")
db = client['test-db']

c = Consumer({
    'bootstrap.servers' : '192.168.35.145',
    'group.id' : 'my-group',
    'auto.offset.reset' : 'earliest',
})
c.subscribe(['temp_test','imgtest'])

while True:
    msg = c.poll()
    if msg.error():
        print("consumer error: {}".format(msg.error()))
        continue
    if msg.topic() == "temp_test":
        collection = 'temperature'
    elif msg.topic() == "imgtest":
        print("done!")
        collection = 'image-test'
    else:
        collection = "no"
    data = loads(msg.value().decode('utf-8'))
    data['datetime'] = datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S')
    print(data)
    db[collection].insert_one(data)
    
        