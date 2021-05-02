import socket

SERVERIO_IP = '127.0.0.1'
SERVERIO_PORTAS = 20000

serverioSoketas = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverioSoketas.bind((SERVERIO_IP, SERVERIO_PORTAS))
serverioSoketas.listen(1)  # vieno kliento

print('Bandome klausyti %s ...' % SERVERIO_PORTAS)

while True:
    kliento_jungtis, kliento_adresas = serverioSoketas.accept()

    uzklausa = kliento_jungtis.recv(1024).decode()
    print(uzklausa)

    atsakas = 'HTTP/1.0 200 OK\n\nLabas, tai atsakymas'
    kliento_jungtis.sendall(atsakas.encode())
    kliento_jungtis.close()

serverioSoketas.close()