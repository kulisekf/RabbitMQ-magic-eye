import numpy as np, cv2
from rabbitmq_connect import connect, open_channel
import os
from dotenv import load_dotenv, find_dotenv

#connect to server
load_dotenv(find_dotenv())
connection = connect(os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"), os.getenv("RABBITMQ_IP_ADDR"), os.getenv("RABBITMQ_PORT"))
channel = open_channel(connection, os.getenv("RABBITMQ_QUEUE_1"))
channel2 = open_channel(connection, os.getenv("RABBITMQ_QUEUE_2"))

def main():
    # subscribe to receive messages from the first queue
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(os.getenv("RABBITMQ_QUEUE_1"), on_receive, auto_ack=False)

    print('Waiting for messages. To exit press CTRL+C')
    print("...")
    channel.start_consuming()

# callback function called when a message is received
def on_receive(ch, method, properties, body):
    print("New task started")

    sharpen_img = sharpen(body)
    #send a message with the direct strategy - image to second queue
    channel2.basic_publish(exchange='', routing_key=os.getenv("RABBITMQ_QUEUE_2"), body=sharpen_img)

    print("Processing done")
    ch.basic_ack(delivery_tag = method.delivery_tag) #Process confirm message

#function that sharp the photo
def sharpen(img):
    # OpenCV load image from byte string
    nparr = np.frombuffer(img, np.uint8)
    im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) # filter definition
    im = cv2.filter2D(im, -1, kernel) # apply filter on image

    img_str = cv2.imencode('.jpeg', im)[1].tobytes() #convert OpenCV image to byte string
    return img_str

if __name__ == "__main__":
    main()