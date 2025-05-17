import Pyro4
import argparse

insultos = []

@Pyro4.expose
class InsultService:
    def recibir_insulto(self, insulto):
        if insulto not in insultos:
            insultos.append(insulto)
            return f"Insulto '{insulto}' añadido."
        else:
            return f"El insulto '{insulto}' ya está en la lista."

    def obtener_insultos(self):
        return insultos

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Iniciar el servicio InsultService PyRO con número de instancia.")
    parser.add_argument('instance_num', type=int, help="Número de instancia para registrar el servicio.")
    args = parser.parse_args()

    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    insult_service = InsultService()
    uri = daemon.register(insult_service)
    name = f"insult.service.{args.instance_num}"
    ns.register(name, uri)

    print(f"InsultService instancia {args.instance_num} corriendo con nombre '{name}'")
    daemon.requestLoop()
