import pika

#provides a connection to the server
def connect(username, password, IPaddr, port):
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(IPaddr, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    return connection
 
#connect the specified channel
def open_channel(connection, queue_name):
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    return channel