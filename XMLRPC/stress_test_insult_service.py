import multiprocessing
import subprocess
import time
import xmlrpc.client

requests = [1, 5, 10, 20]  # Tamaños de carga

def start_insult_service(port):
    """Lanza InsultService en un puerto determinado usando subprocess."""
    return subprocess.Popen(['python', 'XMLRPC/InsultService.py', str(port)])

def test_insult_service(port, num_requests):
    """Envía insultos al servicio XMLRPC y mide tiempo total."""
    insults = ["tonto", "bobo", "puta", "idiota", "cabron"]
    proxy = xmlrpc.client.ServerProxy(f"http://localhost:{port}")
    
    start_time = time.time()
    for i in range(num_requests):
        insult = insults[i % len(insults)]
        proxy.recibir_insulto(insult)
    end_time = time.time()
    
    return end_time - start_time

def calculate_speedup(time_single, time_multi):
    if time_multi > 0:
        return time_single / time_multi
    return 0

def execute_multiple_nodes_test():
    with open("XMLRPC/test_results_m.txt", "w") as file:
        file.write("Resultados de pruebas XMLRPC - Múltiples Nodos:\n\n")

        for num_nodes in [1, 2, 3]:
            # Lanzar servicios InsultService en puertos consecutivos empezando por 8000
            processes = []
            base_port = 8000
            for i in range(num_nodes):
                p = start_insult_service(base_port + i)
                processes.append(p)

            # Esperar que los servicios arranquen
            time.sleep(5)

            for n in requests:
                file.write(f"Test con {num_nodes} nodo(s) y {n} solicitudes\n")

                if num_nodes == 1:
                    # Test para 1 nodo
                    time_single = test_insult_service(base_port, n)
                    speedup = 1.0
                else:
                    # Para múltiples nodos, lanzar test y repartir carga round-robin
                    # Para simplificar aquí llamamos a test_insult_service para cada nodo con n/num_nodes solicitudes
                    times = []
                    requests_per_node = n // num_nodes
                    remainder = n % num_nodes
                    for i in range(num_nodes):
                        requests_to_send = requests_per_node + (remainder if i == num_nodes - 1 else 0)
                        t = test_insult_service(base_port + i, requests_to_send)
                        times.append(t)
                    time_multi = max(times)  # Consideramos el tiempo máximo entre nodos (cuello de botella)
                    speedup = calculate_speedup(time_single, time_multi)

                file.write(f"Tiempo: {time_single if num_nodes == 1 else time_multi:.5f} segundos\n")
                file.write(f"Speedup: {speedup:.5f}\n\n")

                print(f"[Nodos: {num_nodes}] {n} solicitudes -> Tiempo: {time_single if num_nodes == 1 else time_multi:.5f}s, Speedup: {speedup:.5f}")

            # Terminar todos los procesos abiertos
            for p in processes:
                p.terminate()
                p.wait()

if __name__ == "__main__":
    execute_multiple_nodes_test()
