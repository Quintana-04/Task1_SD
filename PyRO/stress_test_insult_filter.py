import Pyro4
import time
import random
import matplotlib.pyplot as plt

def create_proxy(uri):
    return Pyro4.Proxy(uri)

def stress_test_insult_filter_async(uri_filter, uri_insult, num_requests=1000):
    """Simula una prueba de estrés enviando frases con insultos al InsultFilter asíncrono."""
    filter_service = create_proxy(uri_filter)
    insult_service = create_proxy(uri_insult)

    # Paso 1: Publicar insultos en el servicio central (si es necesario)
    insults_to_censor = ["puto", "cabron", "payaso", "idiota", "estupido"]
    for insult in insults_to_censor:
        insult_service.recibir_insulto(insult)
    print(f" [*] Insults published to insult.service: {insults_to_censor}")

    # Paso 2: Generar frases con insultos y enviarlas al filtro
    texts_to_filter = [f"Eres un {random.choice(insults_to_censor)} tonto" for _ in range(num_requests)]

    start_time = time.time()
    for text in texts_to_filter:
        filter_service.agregar_frase_a_cola(text)
    end_time = time.time()

    # Paso 3: Esperar a que todas las frases se procesen
    time.sleep(2 + num_requests / 1000)  # Ajuste proporcional para permitir procesamiento

    resultados = filter_service.obtener_resultados()
    processed_count = len(resultados)

    total_time = end_time - start_time
    if total_time == 0:
        total_time = 1

    throughput = processed_count / total_time
    print(f"Processed {processed_count} texts in {total_time:.2f} seconds.")
    print(f"Throughput: {throughput:.2f} texts per second.")
    return total_time, throughput

def generate_performance_graph(results, num_requests_list):
    throughput = [result[1] for result in results]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(num_requests_list, throughput, 'm-', label='Throughput (texts per second)')

    ax1.set_xlabel('Number of Texts Sent')
    ax1.set_ylabel('Throughput (texts per second)', color='m')
    plt.title('Performance of PyRO (async) with InsultFilter')
    ax1.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

# URIs del servicio InsultFilter e InsultService
uri_filter = "PYRO:insult.filter@localhost:9090"
# Obtener URIs dinámicamente desde el Name Server
ns = Pyro4.locateNS()
uri_filter = ns.lookup("insult.filter")
uri_insult = ns.lookup("insult.service")


# Pruebas con diferentes volúmenes
results = []
num_requests_list = [1000, 5000, 10000, 20000]

for num_requests in num_requests_list:
    print(f"Running test with {num_requests} texts...")
    result_pyro = stress_test_insult_filter_async(uri_filter, uri_insult, num_requests=num_requests)
    results.append(result_pyro)

# Generar la gráfica
generate_performance_graph(results, num_requests_list)
