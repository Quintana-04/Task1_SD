import xmlrpc.client

# Conectar al servidor InsultService
insult_service = xmlrpc.client.ServerProxy('http://localhost:8000/', allow_none=True)

# Enviar insultos
print(insult_service.recibir_insulto("maldito"))
print(insult_service.recibir_insulto("estúpido"))

# Obtener la lista de insultos
insultos = insult_service.obtener_insultos()
print("Lista de insultos:", insultos)

# Conectar al servidor InsultFilter
insult_filter = xmlrpc.client.ServerProxy('http://localhost:9000/', allow_none=True)

# Enviar frases para filtrar
insult_filter.agregar_frase_a_cola("Eres un maldito estúpido.")
insult_filter.agregar_frase_a_cola("Eres un idiota.")

# Obtener los resultados filtrados
resultados = insult_filter.obtener_resultados()
print("Resultados filtrados:", resultados)
