# Task1_SD
05/05/2025:
    - REDIS:
        - Iniciar el servidor con "sudo systemctl start redis-server"

    -RabitMQ:
        - Importante ejecutar primero esta comanda (docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4-management) para iniciar el docker para la comunicacion.
        - Hacer que no guarde insultos repetidos en la lista

    - PyRO
        - Iniciar el Name Server con "Pyro4-ns"