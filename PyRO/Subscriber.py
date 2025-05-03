import Pyro4

@Pyro4.expose
class Subscriber:
    def __init__(self, name):
        self.name = name

    def receive_insult(self, insulto):
        print(f"{self.name} ha recibido el insulto: {insulto}")
