import subprocess
import time
import xmlrpc.client

requests = [1, 5, 10, 20]
insults = ["tonto", "bobo", "puta", "idiota", "cabron"]

def start_insult_service(port):
    return subprocess.Popen(['python', 'XMLRPC/InsultService.py', str(port)])

def start_insult_filter(port):
    return subprocess.Popen(['python', 'XMLRPC/InsultFilter.py', str(port)])

def test_insult_filter(port, num_requests):
    frases = [
        "Eres un tonto y bobo",
        "No seas puta idiota",
        "Qué cabron más grande",
        "Este es un insulto tonto",
        "Bobo cabron idiota"
    ]
    proxy = xmlrpc.client.ServerProxy(f"http://localhost:{port}")

    start_time = time.time()
    for i in range(num_requests):
        frase = frases[i % len(frases)]
        proxy.agregar_frase_a_cola(frase)
    end_time = time.time()

    return end_time - start_time

def calculate_speedup(time_single, time_multi):
    if time_multi > 0:
        return time_single / time_multi
    return 0

def execute_multiple_nodes_test():
    # Lanzar InsultService único
    insult_service_process = start_insult_service(8000)
    time.sleep(3)  # Esperar que arranque

    # Conectarse para añadir insultos
    insult_service_proxy = xmlrpc.client.ServerProxy("http://localhost:8000")
    for insulto in insults:
        insult_service_proxy.recibir_insulto(insulto)

    with open("XMLRPC/test_results_m.txt", "w") as file:
        file.write("Resultados de pruebas XMLRPC - Múltiples Nodos InsultFilter:\n\n")

        for num_nodes in [1, 2, 3]:
            processes = []
            base_port = 9000
            for i in range(num_nodes):
                p = start_insult_filter(base_port + i)
                processes.append(p)

            time.sleep(5)  # Esperar que arranquen los filtros

            for n in requests:
                file.write(f"Test con {num_nodes} nodo(s) y {n} solicitudes\n")

                if num_nodes == 1:
                    time_single = test_insult_filter(base_port, n)
                    speedup = 1.0
                else:
                    times = []
                    requests_per_node = n // num_nodes
                    remainder = n % num_nodes
                    for i in range(num_nodes):
                        requests_to_send = requests_per_node + (remainder if i == num_nodes - 1 else 0)
                        t = test_insult_filter(base_port + i, requests_to_send)
                        times.append(t)
                    time_multi = max(times)
                    speedup = calculate_speedup(time_single, time_multi)

                file.write(f"Tiempo: {time_single if num_nodes == 1 else time_multi:.5f} segundos\n")
                file.write(f"Speedup: {speedup:.5f}\n\n")

                print(f"[Nodos: {num_nodes}] {n} solicitudes -> Tiempo: {time_single if num_nodes == 1 else time_multi:.5f}s, Speedup: {speedup:.5f}")

            for p in processes:
                p.terminate()
                p.wait()

    insult_service_process.terminate()
    insult_service_process.wait()

if __name__ == "__main__":
    execute_multiple_nodes_test()
