import time
import subprocess
import os
import xmlrpc.client

def write_to_both(message, file):
    """Escribe el mensaje tanto en la terminal como en el archivo."""
    print(message)
    file.write(message + "\n")

def send_insults(proxy, num_tasks, insults, file):
    """Envía insultos al InsultService."""
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        proxy.recibir_insulto(insult)

def send_texts(proxy, num_tasks, file):
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
    """Inicia el proceso del InsultService usando subprocess."""
    return subprocess.Popen(['python', 'XMLRPC/InsultService.py', '8000'])

def start_insult_filter():
    """Inicia el proceso del InsultFilter usando subprocess."""
    return subprocess.Popen(['python', 'XMLRPC/InsultFilter.py', '9000'])

def test_insult_service(proxy, num_tasks_list, insults, file):
    """Test de rendimiento para InsultService."""
    results = []
    for n in num_tasks_list:
        start_time = time.time()
        send_insults(proxy, n, insults, file)
        end_time = time.time()
        elapsed_time = end_time - start_time
        result_message = f"Enviados {n} insultos en {elapsed_time:.5f} segundos."
        results.append(result_message)
        write_to_both(result_message, file)
    return results

def test_insult_filter(proxy, num_tasks_list, file):
    """Test de rendimiento para InsultFilter."""
    results = []
    for n in num_tasks_list:
        send_texts(proxy, n, file)
        start_time = time.time()
        # Dejamos 5 segundos para que el hilo de procesamiento haga su trabajo
        time.sleep(5)
        end_time = time.time()
        elapsed_time = end_time - start_time
        result_message = f"Censurados {n} textos en {elapsed_time:.5f} segundos."
        results.append(result_message)
        write_to_both(result_message, file)
    return results

def execute_tests(proxy_service, proxy_filter, num_tasks_list, insults):
    """Ejecuta todos los tests de InsultService y InsultFilter."""
    if not os.path.exists("XMLRPC"):
        os.makedirs("XMLRPC")

    with open("XMLRPC/test_results_s.txt", "w") as file:
        file.write("Resultados de las pruebas (Single Node XMLRPC):\n")
        file.write("\n** Resultados de InsultService **\n")
        test_insult_service(proxy_service, num_tasks_list, insults, file)
        file.write("\n** Resultados de InsultFilter **\n")
        test_insult_filter(proxy_filter, num_tasks_list, file)

def terminate_services(proc_service, proc_filter):
    """Finaliza los procesos de InsultService e InsultFilter."""
    proc_service.terminate()
    proc_filter.terminate()
    print("Procesos de InsultService y InsultFilter terminados.")

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

    # Añade insultos iniciales
    for insult in insults:
        proxy_service.recibir_insulto(insult)

    # Ejecuta los tests
    execute_tests(proxy_service, proxy_filter, num_tasks, insults)

    # Finaliza los procesos
    terminate_services(proc_service, proc_filter)
