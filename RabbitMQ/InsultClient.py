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

# Declara las colas
declare_queue(channel, 'insults_to_censor')
declare_queue(channel, 'texts_to_filter')

# Publica los insultos a censurar
insults_to_censor = ["puto", "cabron", "payaso"]
publish_message(channel, 'insults_to_censor', insults_to_censor)

# Publica los textos para filtrar
texts_to_filter = ["Eres un puto tonto", "Este cabron no para de hablar", "Ese payaso me hace reir"]
publish_message(channel, 'texts_to_filter', texts_to_filter)

# Cierra la conexión
close_connection(connection)
