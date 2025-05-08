import pika

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_channel(connection):
    return connection.channel()

def declare_queue(channel, queue_name='hello'):
    channel.queue_declare(queue=queue_name)

def publish_message(channel, queue_name, messages):
    for message in messages:
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        print(f" [x] Sent '{message}'")

def close_connection(connection):
    connection.close()

# Establece la conexión
connection = create_connection()
channel = create_channel(connection)

# Declara la cola
declare_queue(channel)

# Publica un mensaje
queue_name= 'hello'
messages = ["puto", "cabron", "payaso"]
publish_message(channel, queue_name, messages)

# Cierra la conexión
close_connection(connection)
