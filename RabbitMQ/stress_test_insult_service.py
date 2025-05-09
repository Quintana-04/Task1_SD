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

def publish_message(channel, queue_name, message):
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)

def stress_test_insult_service(num_requests=1000):
    """Simula una prueba de estrés enviando una cantidad de solicitudes."""
    connection = create_connection()
    channel = create_channel(connection)
    declare_queue(channel, 'insults_to_censor')

    start_time = time.time()
    
    # Enviar solicitudes
    for _ in range(num_requests):
        insult = random.choice(["puto", "cabron", "payaso", "idiota", "estupido"])
        publish_message(channel, 'insults_to_censor', insult)

    end_time = time.time()

    total_time = end_time - start_time
    throughput = num_requests / total_time  # Throughput: Insultos procesados por segundo
    print(f"Processed {num_requests} insults in {total_time:.2f} seconds.")
    print(f"Throughput: {throughput:.2f} insults per second.")

    # Return the throughput to use in the plot later
    return throughput

def generate_performance_graph(results, num_requests_list):
    """Genera una gráfica de rendimiento para RabbitMQ mostrando throughput vs número de insultos."""
    # La lista de resultados ya tiene el throughput de cada prueba
    throughput = [result for result in results]  # Extraemos el throughput

    # Crear el gráfico
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(num_requests_list, throughput, 'b-', label='Throughput (insults per second)')

    ax1.set_xlabel('Number of Insults Sent')
    ax1.set_ylabel('Throughput (insults per second)', color='b')

    # Títulos y leyendas
    plt.title('Performance of RabbitMQ with InsultService')
    ax1.legend(loc='upper left')

    # Ajuste del diseño para que todo quede bien visible
    plt.tight_layout()

    # Mostrar el gráfico
    plt.show()

# Realizar las pruebas para RabbitMQ con diferentes cantidades de insultos
results = []
num_requests_list = [1000, 5000, 10000, 20000]  # Diferentes números de insultos para las pruebas

# Ejecutamos las pruebas para cada cantidad de insultos
for num_requests in num_requests_list:
    print(f"Running test with {num_requests} insults...")
    result_rabbitmq = stress_test_insult_service(num_requests=num_requests)
    results.append(result_rabbitmq)

# Generar el gráfico con los resultados de las pruebas
generate_performance_graph(results, num_requests_list)
