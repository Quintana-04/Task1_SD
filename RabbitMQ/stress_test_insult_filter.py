import pika
import time
import random
import matplotlib.pyplot as plt

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def create_channel(connection):
    return connection.channel()

def declare_queue(channel, queue_name='hello'):
    channel.queue_declare(queue=queue_name)

def publish_message(channel, queue_name, messages):
    """Publica los mensajes en la cola especificada"""
    for message in messages:
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        #print(f" [x] Sent '{message}'")

def stress_test_insult_filter(num_requests=1000):
    """Simula una prueba de estrés enviando textos con insultos para ser censurados."""
    connection = create_connection()
    channel = create_channel(connection)

    # Primero, se publican los insultos
    insults_to_censor = ["puto", "cabron", "payaso", "idiota", "estupido"]
    declare_queue(channel, 'insults_to_censor')  # Declarar la cola de insultos
    publish_message(channel, 'insults_to_censor', insults_to_censor)
    print(f" [*] Published insults to be censored: {insults_to_censor}")

    # Luego, se publican los textos para filtrar
    declare_queue(channel, 'texts_to_filter')  # Declarar la cola de textos
    texts_to_filter = [f"Eres un {random.choice(insults_to_censor)} tonto" for _ in range(num_requests)]
    publish_message(channel, 'texts_to_filter', texts_to_filter)
    print(f" [*] Published {num_requests} texts to be filtered.")

    start_time = time.time()

    # Asegúrate de dar suficiente tiempo para que el InsultFilter procese los mensajes
    time.sleep(2)  # Esperamos un poco para permitir que los mensajes sean procesados

    end_time = time.time()

    total_time = end_time - start_time

    # Aseguramos que el tiempo total no sea cero
    if total_time == 0:
        total_time = 1  # Asignamos 1 segundo como mínimo para evitar la división por cero

    throughput = num_requests / total_time  # Textos censurados por segundo
    print(f"Processed {num_requests} texts in {total_time:.2f} seconds.")
    print(f"Throughput: {throughput:.2f} texts per second.")

    # Retornamos los resultados para usar en la gráfica más tarde
    return total_time, throughput

def generate_performance_graph(results, num_requests_list):
    """Genera una gráfica de rendimiento para InsultFilter mostrando throughput vs número de textos enviados."""
    throughput = [result[1] for result in results]  # Extraemos el throughput

    # Crear el gráfico
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(num_requests_list, throughput, 'b-', label='Throughput (texts per second)')

    ax1.set_xlabel('Number of Texts Sent')
    ax1.set_ylabel('Throughput (texts per second)', color='b')

    # Títulos y leyendas
    plt.title('Performance of RabbitMQ with InsultFilter')
    ax1.legend(loc='upper left')

    # Ajuste del diseño para que todo quede bien visible
    plt.tight_layout()

    # Mostrar el gráfico
    plt.show()

# Realizar las pruebas para RabbitMQ con diferentes cantidades de textos
results = []
num_requests_list = [1000, 5000, 10000, 20000]  # Diferentes números de textos para las pruebas

# Ejecutamos las pruebas para cada cantidad de textos
for num_requests in num_requests_list:
    print(f"Running test with {num_requests} texts...")
    result_rabbitmq = stress_test_insult_filter(num_requests=num_requests)
    results.append(result_rabbitmq)

# Generar el gráfico con los resultados de las pruebas
generate_performance_graph(results, num_requests_list)
