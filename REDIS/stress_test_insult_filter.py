import redis
import time
import random
import matplotlib.pyplot as plt

def connect_to_redis(host='localhost', port=6379, db=0):
    """Establece una conexión con el servidor Redis."""
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def send_insults_to_queue(client, queue_name, insults):
    """Envía múltiples insultos a la cola especificada en Redis."""
    for insult in insults:
        client.rpush(queue_name, insult)
        print(f"Produced insult: {insult}")

def send_texts_to_queue(client, queue_name, texts):
    """Envía múltiples textos a la cola especificada en Redis."""
    for text in texts:
        client.rpush(queue_name, text)
        #print(f"Produced text: {text}")

def stress_test_insult_filter(num_requests=1000):
    """Simula una prueba de estrés enviando una cantidad de insultos y textos para ser censurados."""
    client = connect_to_redis()
    insult_queue = "INSULTS"  # Cola de insultos en Redis
    text_queue = "TEXT"  # Cola de textos en Redis

    # Generamos insultos a censurar
    insults_to_censor = ["puto", "cabron", "payaso", "idiota", "estupido"]
    
    # Enviamos los insultos a la cola de Redis
    start_time = time.time()
    send_insults_to_queue(client, insult_queue, insults_to_censor)

    # Luego, generamos los textos a filtrar
    texts_to_filter = [f"Eres un {random.choice(insults_to_censor)} tonto" for _ in range(num_requests)]
    send_texts_to_queue(client, text_queue, texts_to_filter)

    end_time = time.time()

    total_time = end_time - start_time
    throughput = num_requests / total_time  # Textos censurados por segundo
    print(f"Processed {num_requests} texts in {total_time:.2f} seconds.")
    print(f"Throughput: {throughput:.2f} texts per second.")

    # Retornamos los resultados para usar en la gráfica más tarde
    return throughput

def generate_performance_graph(results, num_requests_list):
    """Genera una gráfica de rendimiento para Redis mostrando throughput vs número de textos enviados."""
    throughput = [result for result in results]  # Extraemos el throughput

    # Crear el gráfico
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(num_requests_list, throughput, 'b-', label='Throughput (texts per second)')

    ax1.set_xlabel('Number of Texts Sent')
    ax1.set_ylabel('Throughput (texts per second)', color='b')

    # Títulos y leyendas
    plt.title('Performance of Redis with InsultFilter')
    ax1.legend(loc='upper left')

    # Ajuste del diseño para que todo quede bien visible
    plt.tight_layout()

    # Mostrar el gráfico
    plt.show()

# Realizar las pruebas para Redis con diferentes cantidades de textos
results = []
num_requests_list = [1000, 5000, 10000, 20000]  # Diferentes números de textos para las pruebas

# Ejecutamos las pruebas para cada cantidad de textos
for num_requests in num_requests_list:
    print(f"Running test with {num_requests} texts...")
    result_redis = stress_test_insult_filter(num_requests=num_requests)
    results.append(result_redis)

# Generar el gráfico con los resultados de las pruebas
generate_performance_graph(results, num_requests_list)
