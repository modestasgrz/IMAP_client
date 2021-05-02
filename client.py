import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 20000
BUFFER_SIZE = 1024

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creating client socket
clientSocket.connect((SERVER_IP, SERVER_PORT)) #Connecting with server

message = input()

clientSocket.sendall(message.encode())
response = clientSocket.recv(BUFFER_SIZE).decode()

print(response)

clientSocket.close()