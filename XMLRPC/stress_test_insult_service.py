import xmlrpc.client
import time
import random
import matplotlib.pyplot as plt

def stress_test_xmlrpc_insult_service(uri, num_requests=1000):
    """Simula una prueba de estrés enviando insultos a InsultService usando XMLRPC."""
    insult_service = xmlrpc.client.ServerProxy(uri)
    start_time = time.time()

    for _ in range(num_requests):
        insult = random.choice(["puto", "cabron", "payaso", "idiota", "estupido"])
        insult_service.recibir_insulto(insult)

    end_time = time.time()
    total_time = end_time - start_time
    throughput = num_requests / total_time
    print(f"Processed {num_requests} insults in {total_time:.2f} seconds.")
    print(f"Throughput: {throughput:.2f} insults per second.")
    return throughput

def generate_performance_graph(results, num_requests_list):
    throughput = [r for r in results]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(num_requests_list, throughput, 'r-', label='Throughput (insults per second)')

    ax1.set_xlabel('Number of Insults Sent')
    ax1.set_ylabel('Throughput (insults per second)', color='r')
    plt.title('Performance of XMLRPC with InsultService')
    ax1.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

# Dirección del servicio InsultService XMLRPC
uri = "http://localhost:8000"

results = []
num_requests_list = [10, 50, 100, 200]

for num_requests in num_requests_list:
    print(f"Running test with {num_requests} insults...")
    result = stress_test_xmlrpc_insult_service(uri, num_requests=num_requests)
    results.append(result)

generate_performance_graph(results, num_requests_list)
