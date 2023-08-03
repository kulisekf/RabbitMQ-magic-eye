from rabbitmq_connect import connect, open_channel
import datetime, os
from dotenv import load_dotenv, find_dotenv

def main():
    #connect to server - queue with sharp photo
    load_dotenv(find_dotenv())
    connection = connect(os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"), os.getenv("RABBITMQ_IP_ADDR"), os.getenv("RABBITMQ_PORT"))
    channel = open_channel(connection, os.getenv("RABBITMQ_QUEUE_2"))
    # subscribe to receive messages from the second queue
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(os.getenv("RABBITMQ_QUEUE_2"), on_receive, auto_ack=False)

    print('Waiting for messages. To exit press CTRL+C')
    print("...")
    channel.start_consuming()

# callback function called when a message is received
def on_receive(ch, method, properties, body):
    print("New task started")
    # current time - to create image title
    now = datetime.datetime.now() 
    time = now.strftime("%H_%M_%S_%f")
    file = os.getenv("RABBITMQ_RESULT") + time + ".jpeg"
    #save image
    with open(file, 'wb') as file:
            file.write(body)
    print("Processing done")
    ch.basic_ack(delivery_tag = method.delivery_tag) #Process confirm message

if __name__ == "__main__":
    main()