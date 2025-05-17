import Pyro4
from queue import Queue
import threading
import time

work_queue = Queue()
resultados_filtrados = []

@Pyro4.expose
class InsultFilter:
    def __init__(self, instance_num):
        self.instance_num = instance_num

    def agregar_frase_a_cola(self, frase):
        if frase:
            work_queue.put(frase)
            return "Frase añadida a la cola."
        else:
            return "La frase está vacía, no se ha añadido a la cola."

    def obtener_resultados(self):
        return resultados_filtrados

def procesar_cola(instance_num):
    ns = Pyro4.locateNS()
    insult_service_uri = ns.lookup(f"insult.service.{instance_num}")
    insult_service = Pyro4.Proxy(insult_service_uri)

    while True:
        if not work_queue.empty():
            frase = work_queue.get()
            insultos = insult_service.obtener_insultos()
            for insulto in insultos:
                frase = frase.replace(insulto, "CENSORED")
            resultados_filtrados.append(frase)
            print(f"Frase filtrada: {frase}")
        else:
            time.sleep(0.1)  # Pequeña espera para no consumir CPU sin necesidad

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python InsultFilter.py <instance_num>")
        sys.exit(1)
    instance_num = sys.argv[1]

    insult_filter = InsultFilter(instance_num)
    daemon = Pyro4.Daemon()
    uri = daemon.register(insult_filter)

    ns = Pyro4.locateNS()
    ns.register(f"insult.filter.{instance_num}", uri)

    filter_thread = threading.Thread(target=procesar_cola, args=(instance_num,))
    filter_thread.daemon = True
    filter_thread.start()

    print(f"InsultFilter instancia {instance_num} corriendo y registrada como 'insult.filter.{instance_num}'...")
    daemon.requestLoop()
