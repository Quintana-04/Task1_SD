from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer
from queue import Queue
import threading

# Conectar al servicio InsultService a través de XMLRPC
insult_service = ServerProxy('http://localhost:8000')

resultados_filtrados = []
work_queue = Queue()

# Función para filtrar una frase, reemplazando los insultos por "CENSORED"
def filtrar_frase(frase):
    insultos = insult_service.obtener_insultos()
    
    for insulto in insultos:
        frase = frase.replace(insulto, "CENSORED")
    return frase

# Función para agregar frases a la cola de trabajo
def agregar_frase_a_cola(frase):
    if frase:  # Si la frase no está vacía
        work_queue.put(frase)
        return "Frase añadida a la cola."
    else:
        return "La frase está vacía, no se ha añadido a la cola."

# Función para procesar la cola de trabajo (trabajo en segundo plano)
def procesar_cola():
    while True:
        if not work_queue.empty():
            frase = work_queue.get()
            frase_filtrada = filtrar_frase(frase)
            resultados_filtrados.append(frase_filtrada)
            print(f"Frase filtrada: {frase_filtrada}")

# Función para devolver los resultados filtrados
def obtener_resultados():
    return resultados_filtrados

# Iniciar un hilo para procesar las frases de la cola
thread = threading.Thread(target=procesar_cola)
thread.daemon = True
thread.start()

# Crear el servidor XMLRPC
server = SimpleXMLRPCServer(('localhost', 9000))
server.register_function(agregar_frase_a_cola, 'agregar_frase_a_cola')
server.register_function(obtener_resultados, 'obtener_resultados')

print("InsultFilter corriendo en http://localhost:9000/")
server.serve_forever()
