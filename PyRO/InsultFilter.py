import Pyro4
from queue import Queue
import threading

# Lista de insultos (estos insultos se deben cargar dinámicamente desde InsultService)
insultos = ["maldito", "idiota", "estúpido", "imbécil"]  # Agrega más insultos si es necesario
resultados_filtrados = []
work_queue = Queue()

@Pyro4.expose
class InsultFilter:
    def filtrar_frase(self, frase):
        for insulto in insultos:
            frase = frase.replace(insulto, "CENSORED")
        return frase

    def agregar_frase_a_cola(self, frase):
        if frase:  # Si la frase no está vacía
            work_queue.put(frase)
            return "Frase añadida a la cola."
        else:
            return "La frase está vacía, no se ha añadido a la cola."

    def obtener_resultados(self):
        return resultados_filtrados


def procesar_cola():
    while True:
        if not work_queue.empty():
            frase = work_queue.get()
            frase_filtrada = insult_filter.filtrar_frase(frase)
            resultados_filtrados.append(frase_filtrada)
            print(f"Frase filtrada: {frase_filtrada}")

# Crear y registrar el servicio en Pyro
insult_filter = InsultFilter()
daemon = Pyro4.Daemon()
uri = daemon.register(insult_filter)
ns = Pyro4.locateNS()
ns.register("insult.filter", uri)

# Iniciar el hilo para procesar la cola
filter_thread = threading.Thread(target=procesar_cola)
filter_thread.daemon = True
filter_thread.start()

print("InsultFilter corriendo...")
daemon.requestLoop()
