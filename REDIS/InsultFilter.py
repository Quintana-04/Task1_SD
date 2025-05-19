import redis
import re
import time
import threading

def connect_to_redis(host='localhost', port=6379, db=0):
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

def get_all_insults(client, queue_name_insults, insults):
    while True:
        insult = client.blpop(queue_name_insults, timeout=0)
        if insult:
            insults.append(insult[1])
            # print(f"Insulto almacenado en InsultFilter: {insult[1]}")
        # Puedes agregar condición para salir si quieres

def process_text(client, queue_name_text, insults):
    while True:
        task = client.blpop(queue_name_text, timeout=0)
        if task:
            text = task[1]
            # print(f"Texto recibido: {text}")
            for insult in insults:
                # Censurar insultos usando expresiones regulares para palabras completas
                text = re.sub(r'\b' + re.escape(insult) + r'\b', "CENSORED", text)
            # print(f"Texto censurado: {text}")
            # Opcional: almacenar o enviar el texto procesado a otra cola

def main():
    client = connect_to_redis()
    queue_name_text = "TEXT"
    queue_name_insults = "INSULTS_FILTER"

    insults = []

    insult_thread = threading.Thread(target=get_all_insults, args=(client, queue_name_insults, insults))
    text_thread = threading.Thread(target=process_text, args=(client, queue_name_text, insults))

    insult_thread.start()
    text_thread.start()

    insult_thread.join()
    text_thread.join()

if __name__ == "__main__":
    main()
