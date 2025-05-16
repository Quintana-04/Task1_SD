import pika
import threading
import time
import re

# Lista local para almacenar los insultos a censurar
insults_list = []

def create_connection():
    """Crea una nueva conexión a RabbitMQ"""
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_channel(connection):
    """Crea un canal en RabbitMQ"""
    return connection.channel()

def declare_queue(channel, queue_name='hello'):
    """Declara la cola en RabbitMQ"""
    channel.queue_declare(queue=queue_name)

def store_insults(insults):
    """Almacena los insultos en la lista local"""
    for insult in insults:
        if insult not in insults_list:
            insults_list.append(insult)
            #print(f" [x] Stored insult: {insult}")

def filter_text(text, insults_list):
    """Filtra los insultos en los textos y los reemplaza por 'CENSORED'"""
    original_text = text
    for insult in insults_list:
        text = text.replace(insult, "CENSORED")
    return original_text, text  # Retornamos el texto original y el filtrado

def callback_insults(ch, method, properties, body):
    """Función que maneja los insultos recibidos (de la cola 'insults_to_censor')"""
    insults = body.decode().split(',')  # Asumimos que los insultos se envían en formato string separado por comas
    store_insults(insults)

def callback_texts(ch, method, properties, body):
    """Función que maneja los textos recibidos (de la cola 'texts_to_filter')"""
    original_text = body.decode()
    #print(f" [x] Received text: {original_text}")
    
    # Filtrar el texto
    original, filtered_text = filter_text(original_text, insults_list)
    
    # Mostrar cómo el texto es censurado
    #print(f" [x] Filtered text: {filtered_text}")

def consume_messages(queue_name, callback):
    """Consume mensajes de una cola en RabbitMQ, utilizando su propio canal"""
    connection = create_connection()
    channel = create_channel(connection)

    declare_queue(channel, queue_name)

    # Usamos basic_consume para empezar a consumir mensajes
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    #print(f' [*] Waiting for messages in {queue_name}. To exit, press CTRL+C')
    channel.start_consuming()

def consume_messages_in_threads():
    """Crea hilos para consumir tanto los insultos como los textos"""
    # Creamos los hilos para consumir insultos y textos simultáneamente
    insults_thread = threading.Thread(target=consume_messages, args=('insults_to_censor', callback_insults))
    texts_thread = threading.Thread(target=consume_messages, args=('texts_to_filter', callback_texts))

    # Iniciamos los hilos
    insults_thread.start()
    texts_thread.start()

    # Esperamos a que ambos hilos terminen
    insults_thread.join()
    texts_thread.join()

# Ejecutamos la función que maneja los hilos
consume_messages_in_threads()
