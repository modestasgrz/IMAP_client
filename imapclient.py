import socket, ssl, time
import email

BUFFER_SIZE = 4096
domainName = "imap.mail.yahoo.com"
domainPort = 993 #993 - IMAP port for safe connections, use 143 for unsecured connections

username = "mifktlab3@yahoo.com"
password = "aguzvnmiqzmjusjr"


def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


def login(username, password, socket):
    cmd = "A1 login " + username + " " + password + "\r\n"
    socket.send(cmd.encode())
    return socket.recv(BUFFER_SIZE)


def namespace(socket):
    cmd = "n namespace\r\n"
    socket.send(cmd.encode())
    return socket.recv(BUFFER_SIZE)


def select(flags, socket):
    cmd = "g21 SELECT " + '"{}"'.format(flags) + "\r\n"
    socket.send(cmd.encode())
    return socket.recv(BUFFER_SIZE)


def list(reference, mailbox_name, socket):
    cmd = "A1 LIST " + '"{}"'.format(reference) + " " + '"{}"'.format(mailbox_name) + "\r\n"
    socket.send(cmd.encode())
    return socket.recv(BUFFER_SIZE)


def fetch(num, flags, socket):
    cmd = "a FETCH " + str(num) + " " + flags + "\r\n" #constructs fetch command
    socket.send(cmd.encode())
    return socket.recv(BUFFER_SIZE)


def search_value(flags, value, socket):
    cmd = "a SEARCH " + flags + ' "{}"'.format(value) + "\r\n"
    socket.send(cmd.encode())
    return socket.recv(BUFFER_SIZE)


def search(flags, socket):
    cmd = "a SEARCH " + flags + "\r\n"
    socket.send(cmd.encode())
    return socket.recv(BUFFER_SIZE)


def extractReceived(msg):
    list = msg.split(b'\r\n')
    del list[0]
    new_string = ""
    for item in list:
        stritem = str(item).replace('b\'', '')
        new_string += (stritem + str('\r\n'))
    return new_string


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((domainName, domainPort))
securedSocket = ssl.create_default_context().wrap_socket(clientSocket, server_hostname = domainName)
print(securedSocket.recv(BUFFER_SIZE))

print(login(username, password, securedSocket))
print(namespace(securedSocket))
print(list('', '*', securedSocket))
print(select('INBOX', securedSocket))
print(fetch('1:*', '(BODY[HEADER.FIELDS (Subject)])', securedSocket))
print(search('UNSEEN', securedSocket))
print(search_value('FROM', 'as', securedSocket)) #Search with value


msg = fetch('3', 'BODY[TEXT]', securedSocket)
print(get_body(email.message_from_string(extractReceived(msg))).decode())

#print(msg)
"""
msg1 = extractReceived(fakeBodyList)

print('\n')
print(get_body(email.message_from_string(msg1)).decode().split('\r\n')[8]) #Contents of email body, works if every message looks analogically
"""
#If email has picture, contents of a body index 8, else - 4