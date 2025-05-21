import time
import subprocess
import os
import xmlrpc.client

# Escribe el mismo mensaje tanto en la consola como en el archivo de salida
def write_to_both(message, file):
    print(message)
    file.write(message + "\n")

# Manda los insultos necesarios al proxy pasado por parámetro
def send_insults(proxy, num_tasks, insults):
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        proxy.recibir_insulto(insult)

# Manda los textos necesarios al proxy pasado por parámetro
def send_texts(proxy, num_tasks):
    texts = [
        "Eres un tonto",
        "Que bobo eres",
        "Eres una puta",
        "Eres un idiota",
        "Que cabron eres"
    ]
    for i in range(num_tasks):
        text = texts[i % len(texts)]
        proxy.agregar_frase_a_cola(text)


def start_insult_service():
    return subprocess.Popen(['python', 'XMLRPC/InsultService.py', '8000'])

def start_insult_filter():
    return subprocess.Popen(['python', 'XMLRPC/InsultFilter.py', '9000'])

# Envia insultos al InsultService y calcula el tiempo que tarda
def test_insult_service(proxy, num_tasks_list, insults, file):
    results = []
    for n in num_tasks_list:
        start_time = time.time()
        send_insults(proxy, n, insults)
        end_time = time.time()
        elapsed_time = end_time - start_time
        result_message = f"Enviados {n} insultos en {elapsed_time:.5f} segundos."
        results.append(result_message)
        write_to_both(result_message, file)
    return results

# Envia textos al InsultFilter y calcula el tiempo que tarda
def test_insult_filter(proxy, num_tasks_list, file):
    results = []
    for n in num_tasks_list:
        start_time = time.time()
        send_texts(proxy, n)
        end_time = time.time()
        elapsed_time = end_time - start_time
        result_message = f"Censurados {n} textos en {elapsed_time:.5f} segundos."
        results.append(result_message)
        write_to_both(result_message, file)
    return results

# Ejecuta los tests del InsultService y del InsultFilter
def execute_tests(proxy_service, proxy_filter, num_tasks_list, insults):
    if not os.path.exists("XMLRPC"):
        os.makedirs("XMLRPC")

    with open("XMLRPC/test_results_s.txt", "w") as file:
        file.write("Resultados de las pruebas (Single Node XMLRPC):\n")
        file.write("\n** Resultados de InsultService **\n")
        test_insult_service(proxy_service, num_tasks_list, insults, file)
        file.write("\n** Resultados de InsultFilter **\n")
        test_insult_filter(proxy_filter, num_tasks_list, file)

# Terminar todos los procesos
def terminate_services(proc_service, proc_filter):
    proc_service.terminate()
    proc_filter.terminate()
    print("Procesos de InsultService y InsultFilter terminados.")

# Programa principal
if __name__ == "__main__":
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks = [1, 5, 10, 20]

    # Inicia los servicios
    proc_service = start_insult_service()
    proc_filter = start_insult_filter()
    time.sleep(5)

    # Conecta a los proxies
    proxy_service = xmlrpc.client.ServerProxy("http://localhost:8000")
    proxy_filter = xmlrpc.client.ServerProxy("http://localhost:9000")

    # Añade insultos al InsultService
    for insult in insults:
        proxy_service.recibir_insulto(insult)

    # Ejecuta los tests
    execute_tests(proxy_service, proxy_filter, num_tasks, insults)

    # Finaliza los procesos
    terminate_services(proc_service, proc_filter)
