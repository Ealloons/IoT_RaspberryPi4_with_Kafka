import time
from datetime import datetime
import board
import adafruit_dht
from json import dumps
from kafka import KafkaProducer
producer = KafkaProducer(acks=0, compression_type='gzip', bootstrap_servers=['192.168.35.145:9092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8'))
#Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT11(board.D4)
while True:
    try:
         # Print the values to the serial port
         temperature_c = dhtDevice.temperature
         temperature_f = temperature_c * (9 / 5) + 32
         humidity = dhtDevice.humidity
         print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
               .format(temperature_f, temperature_c, humidity))
         now = datetime.now()
         data = {'m_id' : '0',
                 'datetime' : now.strftime("%Y-%m-%d %H:%M:%S"),
                 'temp' : str(temperature_c)}
         producer.send('temp_test', value=data)
         producer.flush()
    except RuntimeError as error:     # Errors happen fairly often, DHT's are hard to read, just keep going
         print(error.args[0])
    time.sleep(8.0)