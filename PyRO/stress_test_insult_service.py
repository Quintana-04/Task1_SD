import Pyro4
import time
import random
import matplotlib.pyplot as plt

def create_proxy(uri):
    return Pyro4.Proxy(uri)

def stress_test_pyro_insult_service(uri, num_requests=1000):
    """Simula una prueba de estrés a través de PyRO enviando insultos directamente al servicio remoto."""
    insult_service = create_proxy(uri)

    start_time = time.time()
    
    # Enviar solicitudes
    for _ in range(num_requests):
        insult = random.choice(["puto", "cabron", "payaso", "idiota", "estupido"])
        insult_service.recibir_insulto(insult)  # Llamada remota al método

    end_time = time.time()

    total_time = end_time - start_time
    throughput = num_requests / total_time  # Throughput: Insultos procesados por segundo
    print(f"Processed {num_requests} insults in {total_time:.2f} seconds.")
    print(f"Throughput: {throughput:.2f} insults per second.")

    return throughput

def generate_performance_graph(results, num_requests_list):
    """Genera una gráfica de rendimiento para PyRO mostrando throughput vs número de insultos."""
    throughput = [result for result in results]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(num_requests_list, throughput, 'g-', label='Throughput (insults per second)')

    ax1.set_xlabel('Number of Insults Sent')
    ax1.set_ylabel('Throughput (insults per second)', color='g')
    plt.title('Performance of PyRO with InsultService')
    ax1.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

# URI del servicio remoto PyRO
ns = Pyro4.locateNS()
pyro_uri = ns.lookup("insult.service")


# Lista de pruebas con diferentes cargas
results = []
num_requests_list = [1000, 5000, 10000, 20000]

for num_requests in num_requests_list:
    print(f"Running test with {num_requests} insults...")
    result_pyro = stress_test_pyro_insult_service(pyro_uri, num_requests=num_requests)
    results.append(result_pyro)

# Generar el gráfico con los resultados
generate_performance_graph(results, num_requests_list)
