import numpy as np, cv2
from rabbitmq_connect import connect, open_channel
import os, pika, logging, sys
from dotenv import load_dotenv, find_dotenv
from log import set_logging

load_dotenv(find_dotenv())
set_logging(os.getenv("RABBITMQ_LOG_LEVEL"))
logging.info("Rabbitmq - Magic eye - sharpening v0.1.0")
logging.info("Logging mode - {}".format(str(os.getenv("RABBITMQ_LOG_LEVEL"))))
try:
    #connect to server
    connection = connect(os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"), os.getenv("RABBITMQ_IP_ADDR"), os.getenv("RABBITMQ_PORT"))
except Exception as e:
    logging.error("Failed to connect to rabbitmq server: " + str(e))
    sys.exit("Failed to connect to rabbitmq server: " + str(e))

try:
    #open channel
    channel = open_channel(connection, os.getenv("RABBITMQ_QUEUE_1"))
    channel2 = open_channel(connection, os.getenv("RABBITMQ_QUEUE_2"))
except Exception as e:
    logging.error("Failed to open rabbitmq channel: " + str(e))
    sys.exit("Failed to open rabbitmq channel: " + str(e))

def main():
    """
    The main function, which specifies consuming and then starts consuming.
    """
    # subscribe to receive messages from the first queue
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(os.getenv("RABBITMQ_QUEUE_1"), on_receive, auto_ack=False)
    logging.debug("Subscribe to receive messages from the queue {}, auto_ack=False, prefetch_count=1".format(str(os.getenv("RABBITMQ_QUEUE_1"))))
    logging.info("Waiting for messages. To exit press CTRL+C")
    logging.info("...")

    channel.start_consuming()

def on_receive(ch: pika.adapters.blocking_connection.BlockingChannel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes)->None:
    """
    Callback function called when a message is received

        :param ch pika.adapters.blocking_connection.BlockingChannel: necessary parameter for the callback function of the Pika library, which provides an interface between the RabbitMQ system and Python
        :param method pika.spec.Basic.Deliver: necessary parameter for the callback function of the Pika library, which provides an interface between the RabbitMQ system and Python
        :param properties pika.spec.BasicProperties: necessary parameter for the callback function of the Pika library, which provides an interface between the RabbitMQ system and Python
        :param body bytes: necessary parameter for the callback function of the Pika library, which provides an interface between the RabbitMQ system and Python - contains the data stored in the queue - here the image data

    """
    try:
        logging.info("New task started")
        sharpen_img = sharpen(body)
        #send a message with the direct strategy - image to second queue
        channel2.basic_publish(exchange='', routing_key=os.getenv("RABBITMQ_QUEUE_2"), body=sharpen_img, properties=pika.BasicProperties(
                            delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
                        ))
        logging.debug("Image inserted into the queue {}".format(str(os.getenv("RABBITMQ_QUEUE_2"))))
        ch.basic_ack(delivery_tag = method.delivery_tag) #Process confirm message
        logging.debug("Process confirm message send")
        logging.info("Processing done")
    except Exception as e:
        add_to_ERROR_queue(e, body)
        ch.basic_ack(delivery_tag = method.delivery_tag) #Process confirm message
        logging.info("Processing done")


def add_to_ERROR_queue(e: Exception, body: bytes)->None:
    """
    if an ERROR condition occurs while working with a queued element (in this case it should be a picture by picture), this function puts the queue element into a new queue named ERROR_queue for later analysis

        :param body bytes: data read from the queue that caused the ERROR
        :param e exception: error content for logging

    """
    logging.error(str(e))
    channel = open_channel(connection, "ERROR_queue")
    channel.basic_publish(exchange='',routing_key="ERROR_queue", body=body, properties=pika.BasicProperties(
                        delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
                    ))
    logging.error("The element that caused error was put into the queue ERROR_queue for later analysis")
    channel.close()

def is_sharp(img: np.ndarray)->np.uint8:
    """
        function that returns the sharpness index of the image

            :param img np.ndarray: image in numpy format that needs to be checked to see if it is sharp

            :returns: value between 0-255 inclusive that determines the sharpness index of the image
            :rtype: np.uint8
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharpIndex = np.max(cv2.convertScaleAbs(cv2.Laplacian(gray, 3)))
    logging.info("Sharpness index value = {}".format(str(sharpIndex)))
    return (sharpIndex)

def sharpen(img: bytes)->bytes:
    """
        function that sharp the photo unless it is sharp

            :param img bytes: the image in bytes format that was loaded from the queue

            :returns: the resulting image in bytes format, which will then be stored in a new queue
            :rtype: bytes
    """
    # OpenCV load image from byte string
    nparr = np.frombuffer(img, np.uint8)
    im = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    logging.debug("Image convert frome byte format to numpy image format")
    if is_sharp(im) <= int(os.getenv("RABBITMQ_SHARPENING_CONSTANT")): #detects sharpness value -> 255 = sharp
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) # filter definition
        im = cv2.filter2D(im, -1, kernel) # apply filter on image
        logging.debug("Image sharpening done")

    img_str = cv2.imencode('.jpeg', im)[1].tobytes() #convert OpenCV image to byte string
    logging.debug("Image convert frome numpy image format to byte format")
    return img_str

if __name__ == "__main__":
    main()