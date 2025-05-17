import subprocess
import time
import os
import xmlrpc.client
import threading

def write_to_both(message, file):
    print(message)
    file.write(message + "\n")

def start_insult_service(port):
    return subprocess.Popen(['python', 'XMLRPC/InsultService.py', str(port)])

def start_insult_filter(port):
    return subprocess.Popen(['python', 'XMLRPC/InsultFilter.py', str(port)])

def send_insults(num_tasks, insults, port, result, idx):
    proxy = xmlrpc.client.ServerProxy(f"http://localhost:{port}")
    start_time = time.time()
    for i in range(num_tasks):
        insult = insults[i % len(insults)]
        proxy.recibir_insulto(insult)
    end_time = time.time()
    result[idx] = end_time - start_time

def send_texts(num_tasks, port, result, idx):
    proxy = xmlrpc.client.ServerProxy(f"http://localhost:{port}")
    texts = [
        "Eres un tonto",
        "Que bobo eres",
        "Eres una puta",
        "Eres un idiota",
        "Que cabron eres"
    ]
    start_time = time.time()
    for _ in range(num_tasks):
        for text in texts:
            proxy.agregar_frase_a_cola(text)
    end_time = time.time()
    result[idx] = end_time - start_time

def calculate_speedup(time_single, time_multi):
    if time_multi > 0:
        return time_single / time_multi
    return 0

def terminate_services(processes):
    for p in processes:
        p.terminate()
        p.wait()

def execute_multiple_nodes_test(num_tasks_list, insults):
    if not os.path.exists("XMLRPC"):
        os.makedirs("XMLRPC")

    with open("XMLRPC/test_results_m.txt", "w") as file:
        file.write("Resultados de las pruebas - Múltiples Nodos (XMLRPC):\n")

        times_service_1node = {}
        times_filter_1node = {}

        for num_nodes in [1, 2, 3]:
            for num_tasks in num_tasks_list:
                file.write(f"\n--- Test con {num_nodes} Nodo(s) y {num_tasks} datos ---\n")

                base_port_service = 8000
                base_port_filter = 9000

                if num_nodes == 1:
                    service_proc = [start_insult_service(base_port_service)]
                    time.sleep(2)
                    
                    # Insertar los insultos en el primer nodo del InsultService
                    proxy = xmlrpc.client.ServerProxy(f"http://localhost:{base_port_service}")
                    for insult in insults:
                        proxy.recibir_insulto(insult)

                    filter_proc = [start_insult_filter(base_port_filter)]
                    time.sleep(5)

                    # Preparar listas para capturar los tiempos
                    service_time_list = [0]
                    filter_time_list = [0]

                    # Medir tiempo total (aunque no es obligatorio)
                    t0 = time.time()
                    send_insults(num_tasks, insults, base_port_service, service_time_list, 0)
                    send_texts(num_tasks, base_port_filter, filter_time_list, 0)
                    t1 = time.time()

                    service_time = service_time_list[0]
                    filter_time = filter_time_list[0]

                    times_service_1node[num_tasks] = service_time
                    times_filter_1node[num_tasks] = filter_time

                    terminate_services(service_proc)
                    terminate_services(filter_proc)

                    write_to_both(f"Tiempo InsultService con {num_nodes} nodos: {service_time:.5f} segundos", file)
                    write_to_both(f"Tiempo InsultFilter con {num_nodes} nodos: {filter_time:.5f} segundos", file)


                else:
                    service_proc = []
                    for i in range(num_nodes):
                        p = start_insult_service(base_port_service + i)
                        service_proc.append(p)

                    time.sleep(2)
                    proxy = xmlrpc.client.ServerProxy(f"http://localhost:{base_port_service}")
                    for insult in insults:
                        proxy.recibir_insulto(insult)

                    filter_proc = []
                    for i in range(num_nodes):
                        p = start_insult_filter(base_port_filter + i)
                        filter_proc.append(p)

                    time.sleep(5)

                    insults_per_node = num_tasks // num_nodes
                    remainder = num_tasks % num_nodes

                    service_threads = []
                    filter_threads = []
                    service_times = [0] * num_nodes
                    filter_times = [0] * num_nodes

                    for i in range(num_nodes):
                        count = insults_per_node + (1 if i == num_nodes - 1 else 0)
                        t1 = threading.Thread(target=send_insults, args=(count, insults, base_port_service + i, service_times, i))
                        t2 = threading.Thread(target=send_texts, args=(count, base_port_filter + i, filter_times, i))
                        service_threads.append(t1)
                        filter_threads.append(t2)

                    start_all = time.time()
                    for t in service_threads + filter_threads:
                        t.start()
                    for t in service_threads + filter_threads:
                        t.join()
                    end_all = time.time()

                    service_time = max(service_times)
                    filter_time = max(filter_times)

                    speedup_service = calculate_speedup(times_service_1node[num_tasks], service_time)
                    speedup_filter = calculate_speedup(times_filter_1node[num_tasks], filter_time)

                    terminate_services(service_proc)
                    terminate_services(filter_proc)

                    write_to_both(f"Tiempo InsultService con {num_nodes} nodos: {service_time:.5f} segundos", file)
                    write_to_both(f"Tiempo InsultFilter con {num_nodes} nodos: {filter_time:.5f} segundos", file)
                    file.write(f"Speedup de InsultService con {num_nodes} nodos: {speedup_service:.5f}\n")
                    file.write(f"Speedup de InsultFilter con {num_nodes} nodos: {speedup_filter:.5f}\n")

if __name__ == "__main__":
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    num_tasks_list = [1, 5, 10, 20]
    execute_multiple_nodes_test(num_tasks_list, insults)
