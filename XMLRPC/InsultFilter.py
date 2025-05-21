from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer
from queue import Queue
import threading
import argparse

insult_service = ServerProxy('http://localhost:8000')
resultados_filtrados = []
work_queue = Queue()

def filtrar_frase(frase):
    insultos = ["tonto", "bobo", "puta", "idiota", "cabron"]
    for insulto in insultos:
        frase = frase.replace(insulto, "CENSORED")
    return frase

def agregar_frase_a_cola(frase):
    work_queue.put(frase)
    return "Frase añadida a la cola."

def procesar_cola():
    while True:
        if not work_queue.empty():
            frase = work_queue.get()
            frase_filtrada = filtrar_frase(frase)
            resultados_filtrados.append(frase_filtrada)
            print(f"Frase filtrada: {frase_filtrada}")

def obtener_resultados():
    return resultados_filtrados

def run_server(port):
    server = SimpleXMLRPCServer(('localhost', port))
    server.register_function(agregar_frase_a_cola, 'agregar_frase_a_cola')
    server.register_function(obtener_resultados, 'obtener_resultados')

    print(f"InsultFilter corriendo en http://localhost:{port}/")
    server.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Iniciar el servicio InsultFilter en el puerto especificado.")
    parser.add_argument('port', type=int, help="Número de puerto en el que el servidor escuchará.")
    args = parser.parse_args()

    thread = threading.Thread(target=procesar_cola)
    thread.daemon = True
    thread.start()

    run_server(args.port)
