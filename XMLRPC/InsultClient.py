import xmlrpc.client

insult_service = xmlrpc.client.ServerProxy('http://localhost:8000/', allow_none=True)

print(insult_service.recibir_insulto("maldito"))
print(insult_service.recibir_insulto("estúpido"))

insultos = insult_service.obtener_insultos()
print("Lista de insultos:", insultos)

insult_filter = xmlrpc.client.ServerProxy('http://localhost:9000/', allow_none=True)

insult_filter.agregar_frase_a_cola("Eres un maldito estúpido.")
insult_filter.agregar_frase_a_cola("Eres un idiota.")

resultados = insult_filter.obtener_resultados()
print("Resultados filtrados:", resultados)
