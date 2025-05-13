import redis
import time
import random
import matplotlib.pyplot as plt

def connect_to_redis(host='localhost', port=6379, db=0):
    """Establece una conexión con el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def send_insults_to_queue(client, queue_name, tasks):
    """Envía múltiples insultos a la cola especificada en Redis"""
    for task in tasks:
        client.rpush(queue_name, task)
        #print(f"Produced: {task}")

def stress_test_insult_service(num_requests=1000):
    """Simula una prueba de estrés enviando una cantidad de insultos a la cola de Redis"""
    client = connect_to_redis()
    queue_name = "INSULTS"  # Nombre de la cola en Redis

    # Generamos una lista de insultos. Generaremos la cantidad necesaria según la prueba
    insults_to_censor = ["puto", "cabron", "payaso", "idiota", "estupido"]

    # Repetir la lista de insultos tantas veces como sea necesario para llegar a num_requests
    insults_to_censor = [random.choice(insults_to_censor) for _ in range(num_requests)]
    
    # Enviar los insultos a la cola
    start_time = time.time()
    send_insults_to_queue(client, queue_name, insults_to_censor)

    end_time = time.time()

    total_time = end_time - start_time
    throughput = num_requests / total_time  # Throughput: Insultos procesados por segundo
    print(f"Processed {num_requests} insults in {total_time:.2f} seconds.")
    print(f"Throughput: {throughput:.2f} insults per second.")

    # Return the throughput to use in the plot later
    return throughput

def generate_performance_graph(results, num_requests_list):
    """Genera una gráfica de rendimiento para Redis mostrando throughput vs número de insultos."""
    throughput = [result for result in results]  # Extraemos el throughput

    # Crear el gráfico
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(num_requests_list, throughput, 'b-', label='Throughput (insults per second)')

    ax1.set_xlabel('Number of Insults Sent')
    ax1.set_ylabel('Throughput (insults per second)', color='b')

    # Títulos y leyendas
    plt.title('Performance of Redis with InsultService')
    ax1.legend(loc='upper left')

    # Ajuste del diseño para que todo quede bien visible
    plt.tight_layout()

    # Mostrar el gráfico
    plt.show()

# Realizar las pruebas para Redis con diferentes cantidades de insultos
results = []
num_requests_list = [1000, 5000, 10000, 20000]  # Diferentes números de insultos para las pruebas

# Ejecutamos las pruebas para cada cantidad de insultos
for num_requests in num_requests_list:
    print(f"Running test with {num_requests} insults...")
    result_redis = stress_test_insult_service(num_requests=num_requests)
    results.append(result_redis)

# Generar el gráfico con los resultados de las pruebas
generate_performance_graph(results, num_requests_list)