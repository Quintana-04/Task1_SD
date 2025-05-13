import xmlrpc.client
import time
import random
import matplotlib.pyplot as plt

def stress_test_xmlrpc_insult_filter(uri_filter, uri_insult, num_requests=1000):
    """Simula una prueba de estrés a través de XMLRPC enviando frases con insultos a InsultFilter."""
    insult_filter = xmlrpc.client.ServerProxy(uri_filter)
    insult_service = xmlrpc.client.ServerProxy(uri_insult)

    insults = ["puto", "cabron", "payaso", "idiota", "estupido"]

    for ins in insults:
        insult_service.recibir_insulto(ins)

    start_time = time.time()

    for _ in range(num_requests):
        insult = random.choice(insults)
        frase = f"Eres un {insult} tonto"
        insult_filter.agregar_frase_a_cola(frase)

    end_time = time.time()
    total_time = end_time - start_time
    throughput = num_requests / total_time
    print(f"Processed {num_requests} texts in {total_time:.2f} seconds.")
    print(f"Throughput: {throughput:.2f} texts per second.")
    return throughput

def generate_performance_graph(results, num_requests_list):
    throughput = [r for r in results]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(num_requests_list, throughput, 'b-', label='Throughput (texts per second)')

    ax1.set_xlabel('Number of Texts Sent')
    ax1.set_ylabel('Throughput (texts per second)', color='b')
    plt.title('Performance of XMLRPC with InsultFilter')
    ax1.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

# Dirección del servicio InsultFilter e InsultService XMLRPC
uri_filter = "http://localhost:9000"
uri_insult = "http://localhost:8000"

results = []
num_requests_list = [10, 50, 100, 200]

for num_requests in num_requests_list:
    print(f"Running test with {num_requests} texts...")
    result = stress_test_xmlrpc_insult_filter(uri_filter, uri_insult, num_requests=num_requests)
    results.append(result)

generate_performance_graph(results, num_requests_list)
