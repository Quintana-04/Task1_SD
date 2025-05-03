import random
import time
import xmlrpc.client
from threading import Thread

# Conectar al servicio InsultService
server = xmlrpc.client.ServerProxy('http://localhost:8000/')

class InsultBroadcaster:
    def __init__(self):
        self.subscribers = []

    def add_subscriber(self, subscriber):
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)
            print("Nuevo suscriptor añadido.")
        else:
            print("Este suscriptor ya está registrado.")

    def remove_subscriber(self, subscriber):
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)
            print("Suscriptor eliminado.")
        else:
            print("Este suscriptor no está registrado.")

    def broadcast_insult(self):
        while True:
            insultos = server.obtener_insultos()
            
            if insultos:
                insulto_random = random.choice(insultos)
                print(f"Broadcasting insulto: {insulto_random}")
                for subscriber in self.subscribers:
                    subscriber.receive_insult(insulto_random)
            else:
                print("No hay insultos en la lista para broadcast.")
            
            time.sleep(5)  # Emitir insulto cada 5 segundos


class InsultSubscriber:
    def __init__(self, name):
        self.name = name

    def receive_insult(self, insulto):
        print(f"{self.name} ha recibido un insulto: {insulto}")


# Crear el broadcaster
broadcaster = InsultBroadcaster()

# Crear suscriptores
subscriber1 = InsultSubscriber("Suscriptor 1")
subscriber2 = InsultSubscriber("Suscriptor 2")

# Añadir suscriptores
broadcaster.add_subscriber(subscriber1)
broadcaster.add_subscriber(subscriber2)

# Iniciar el broadcaster en un hilo separado
broadcast_thread = Thread(target=broadcaster.broadcast_insult)
broadcast_thread.daemon = True
broadcast_thread.start()

# Mantener el programa en ejecución
while True:
    time.sleep(1)
