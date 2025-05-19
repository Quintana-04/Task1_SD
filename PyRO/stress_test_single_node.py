import Pyro4
import subprocess
import time
import os
import threading
import sys

def write_to_both(message, file):
    print(message)
    file.write(message + "\n")

def send_insults(proxy, num_tasks, insults):
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        proxy.recibir_insulto(insult)

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

def start_insult_service(instance_num):
    return subprocess.Popen(['python', 'PYRO/InsultService.py', str(instance_num)])

def start_insult_filter(instance_num):
    return subprocess.Popen(['python', 'PYRO/InsultFilter.py', str(instance_num)])

def test_insult_service(proxy, num_tasks_list, insults, file):
    results = []
    for n in num_tasks_list:
        start_time = time.time()
        send_insults(proxy, n, insults)
        end_time = time.time()
        elapsed = end_time - start_time
        msg = f"Enviados {n} insultos en {elapsed:.5f} segundos."
        results.append(msg)
        write_to_both(msg, file)
    return results

def test_insult_filter(proxy, num_tasks_list, file):
    results = []
    for n in num_tasks_list:
        start_time = time.time()
        send_texts(proxy, n)
        end_time = time.time()
        elapsed = end_time - start_time
        msg = f"Censurados {n} textos en {elapsed:.5f} segundos."
        results.append(msg)
        write_to_both(msg, file)
    return results

def execute_single_node_tests(num_tasks_list, insults):
    if not os.path.exists("PYRO"):
        os.makedirs("PYRO")

    with open("PYRO/test_results_s.txt", "w") as file:
        file.write("Resultados pruebas Single Node PyRO:\n\n")

        # Lanzar servicios instancia 0 (single node)
        service_proc = start_insult_service(0)
        filter_proc = start_insult_filter(0)
        time.sleep(15)  # Esperar que arranquen

        # Conectarse a Nameserver y proxies únicos por instancia
        ns = Pyro4.locateNS()
        proxy_service = Pyro4.Proxy(ns.lookup("insult.service.0"))
        proxy_filter = Pyro4.Proxy(ns.lookup("insult.filter.0"))

        # Inicializar insultos
        for insult in insults:
            proxy_service.recibir_insulto(insult)

        # Ejecutar tests
        test_insult_service(proxy_service, num_tasks_list, insults, file)
        test_insult_filter(proxy_filter, num_tasks_list, file)

        # Terminar servicios
        service_proc.terminate()
        filter_proc.terminate()
        service_proc.wait()
        filter_proc.wait()
        print("Procesos terminados.")

if __name__ == "__main__":
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks_list = [1000, 5000, 10000, 20000]
    execute_single_node_tests(num_tasks_list, insults)
