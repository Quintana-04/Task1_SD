import Pyro4
import random
import time
from threading import Thread
from Subscriber import Subscriber

# Conectar al servicio InsultService
ns = Pyro4.locateNS()
insult_service_uri = ns.lookup("insult.service")
insult_service = Pyro4.Proxy(insult_service_uri)

@Pyro4.expose
class InsultBroadcaster:
    def __init__(self):
        self.subscribers = []

    def add_subscriber(self, subscriber):
        self.subscribers.append(Subscriber(subscriber))
        print(f"Nuevo suscriptor añadido.")

    def remove_subscriber(self, subscriber):
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)
            print(f"Suscriptor eliminado.")
        else:
            print(f"Este suscriptor no está registrado.")

    def broadcast_insult(self):
        while True:
            insultos = insult_service.obtener_insultos()

            if insultos:
                insulto_random = random.choice(insultos)
                print(f"Broadcasting insulto: {insulto_random}")
                for subscriber in self.subscribers:
                    subscriber.receive_insult(insulto_random)  # Llamar al método remoto de suscripción
            else:
                print("No hay insultos en la lista para broadcast.")
            
            time.sleep(5)  # Emitir insulto cada 5 segundos


# Crear y registrar el broadcaster en Pyro
broadcaster = InsultBroadcaster()
daemon = Pyro4.Daemon()
uri = daemon.register(broadcaster)
ns = Pyro4.locateNS()
ns.register("insult.broadcaster", uri)

# Iniciar el hilo para enviar insultos
broadcast_thread = Thread(target=broadcaster.broadcast_insult)
broadcast_thread.daemon = True
broadcast_thread.start()

print("InsultBroadcaster corriendo...")
daemon.requestLoop()