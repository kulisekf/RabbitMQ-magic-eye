import os, pika
from rabbitmq_connect import connect, open_channel
from dotenv import load_dotenv, find_dotenv

def main():
    #connect to server - queue with original photo
    load_dotenv(find_dotenv())
    connection = connect(os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"), os.getenv("RABBITMQ_IP_ADDR"), os.getenv("RABBITMQ_PORT"))
    channel = open_channel(connection, os.getenv("RABBITMQ_QUEUE_1"))

    #for filename in os.listdir(os.getenv("RABBITMQ_ORIGIN")): #for every file in folder
    for filename in os.listdir(os.path.join(os.getcwd(), os.getenv("RABBITMQ_ORIGIN"))): #for every file in folder
        f = os.path.join(os.getenv("RABBITMQ_ORIGIN"), filename) 
        if os.path.isfile(f): # checking if it is a file
            with open(f, "rb") as image:
                f = image.read()
                b = bytearray(f)
                #send a message with the direct strategy
                channel.basic_publish(exchange='', routing_key=os.getenv("RABBITMQ_QUEUE_1"), body=b, properties=pika.BasicProperties(
                         delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
                      ))

    print("sending was successful")
    connection.close()

if __name__ == "__main__":
    main()