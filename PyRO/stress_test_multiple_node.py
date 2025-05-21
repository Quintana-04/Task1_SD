import Pyro4
import subprocess
import time
import os
import threading

# Escribe el mismo mensaje tanto en la consola como en el archivo de salida
def write_to_both(message, file):
    print(message)
    file.write(message + "\n")

# Manda los insultos necesarios al puerto pasado por parámetro y calcula el tiempo que tarda
def send_insults(proxy, num_tasks, insults, result, idx):
    start = time.time()
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        proxy.recibir_insulto(insult)
    end = time.time()
    result[idx] = end - start

# Manda los textos necesarios al puerto pasado por parámetro y calcula el tiempo
def send_texts(proxy, num_tasks, result, idx):
    texts = [
        "Eres un tonto",
        "Que bobo eres",
        "Eres una puta",
        "Eres un idiota",
        "Que cabron eres"
    ]
    start = time.time()
    for i in range(num_tasks):
        text = texts[i % len(texts)]
        proxy.agregar_frase_a_cola(text)
    end = time.time()
    result[idx] = end - start

def start_insult_service(instance_num):
    return subprocess.Popen(['python', 'PYRO/InsultService.py', str(instance_num)])

def start_insult_filter(instance_num):
    return subprocess.Popen(['python', 'PYRO/InsultFilter.py', str(instance_num)])

# Ejecuta los tests del InsultService y del InsultFilter
def execute_multiple_nodes_tests(num_tasks_list, insults):
    if not os.path.exists("PYRO"):
        os.makedirs("PYRO")

    with open("PYRO/test_results_m.txt", "w") as file:
        file.write("Resultados pruebas Multiple Nodes PyRO:\n\n")

        times_service_1node = {}
        times_filter_1node = {}

        for num_nodes in [1, 2, 3]:
            for n in num_tasks_list:
                file.write(f"\n--- Test con {num_nodes} Nodo(s) y {n} datos ---\n")

                # Ejecutar servicios con instancia única
                service_procs = [start_insult_service(i) for i in range(num_nodes)]
                filter_procs = [start_insult_filter(i) for i in range(num_nodes)]

                time.sleep(20)

                # Conectarse al Name Server
                ns = Pyro4.locateNS()

                # Crear proxies para cada instancia
                proxies_service = [Pyro4.Proxy(ns.lookup(f"insult.service.{i}")) for i in range(num_nodes)]
                proxies_filter = [Pyro4.Proxy(ns.lookup(f"insult.filter.{i}")) for i in range(num_nodes)]

                for proxy in proxies_service:
                    for insult in insults:
                        proxy.recibir_insulto(insult)

                # Inicializar listas para los resultados
                service_times = [0] * num_nodes
                filter_times = [0] * num_nodes
                threads = []

                insults_per_node = n // num_nodes
                remainder = n % num_nodes

                # Enviar insultos en paralelo a cada nodo
                for i in range(num_nodes):
                    count = insults_per_node + (remainder if i == num_nodes - 1 else 0)
                    t = threading.Thread(target=send_insults, args=(proxies_service[i], count, insults, service_times, i))
                    threads.append(t)

                # Enviar textos en paralelo a cada nodo
                for i in range(num_nodes):
                    count = insults_per_node + (remainder if i == num_nodes - 1 else 0)
                    t = threading.Thread(target=send_texts, args=(proxies_filter[i], count, filter_times, i))
                    threads.append(t)

                # Ejecutar y esperar a que terminen
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

                service_time = max(service_times)
                filter_time = max(filter_times)

                if num_nodes == 1:
                    times_service_1node[n] = service_time
                    times_filter_1node[n] = filter_time

                # Calcular speedup
                speedup_service = (times_service_1node[n] / service_time) if service_time else 0
                speedup_filter = (times_filter_1node[n] / filter_time) if filter_time else 0

                terminate_services(filter_procs)
                terminate_services(service_procs)

                write_to_both(f"Tiempo InsultService con {num_nodes} nodos: {service_time:.5f} segundos", file)
                write_to_both(f"Tiempo InsultFilter con {num_nodes} nodos: {filter_time:.5f} segundos", file)
                file.write(f"Speedup InsultService con {num_nodes} nodos: {speedup_service:.5f}\n")
                file.write(f"Speedup InsultFilter con {num_nodes} nodos: {speedup_filter:.5f}\n")

# Termina los procesos
def terminate_services(procs):
    for p in procs:
        p.terminate()
        p.wait()
    print("Procesos terminados.")

# Programa principal
if __name__ == "__main__":
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks_list = [1000, 5000, 10000, 20000]
    execute_multiple_nodes_tests(num_tasks_list, insults)
