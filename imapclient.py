import socket, ssl
import email
import os
from email.header import decode_header

BUFFER_SIZE = 1000000
domainName = "imap.mail.yahoo.com"
domainPort = 993 #993 - IMAP port for safe connections, use 143 for unsecured connections

username = "mifktlab3@yahoo.com"
password = "aguzvnmiqzmjusjr"

attachment_dir = 'D:\Modesto\VU\Kompiuteriu_tinklai\Lab3\IMAP_client\Attachments'


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
    full_msg = b''
    while True:
        msg = securedSocket.recv(BUFFER_SIZE)
        full_msg += msg
        if msg.decode().__contains__("a OK FETCH completed"):
            break
    list_msg = full_msg.split(b'\r\n')
    start = list_msg.pop(0)
    end = list_msg.pop()
    data = b'\r\n'.join(list_msg)
    return start, end, data


def search_value(flags, value, socket):
    cmd = "a SEARCH " + flags + ' "{}"'.format(value) + "\r\n"
    socket.send(cmd.encode())
    list_of_results = socket.recv(BUFFER_SIZE).split(b'\r\n')
    list_of_results.pop()
    search_result = list_of_results.pop()
    search_data = list_of_results.pop()
    search_data = search_data.split(b' ')
    search_data.pop(0) #starting sterisk pop out
    search_data.pop(0) #earch command pop out
    search_data.pop() #ending space pop out
    return search_result, search_data


def search(flags, socket):
    cmd = "a SEARCH " + flags + "\r\n"
    socket.send(cmd.encode())
    return socket.recv(BUFFER_SIZE)


def get_attachments(msg):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()

        if bool(fileName): #if attachment == False, the attachment isn't there
            if decode_header(fileName)[0][1] is not None:
                fileName = decode_header(fileName)[0][0].decode(decode_header(fileName)[0][1])
            filePath = os.path.join(attachment_dir, fileName)
            with open(filePath, 'wb') as f:
                f.write(part.get_payload(decode=True))


def list_emails(search_value):
    result, data = search_value
    for i in data:  # this loop works only for search command for now
        num = i.decode()
        start, end, data = fetch(num, '(RFC822)', securedSocket)
        print(get_body(email.message_from_bytes(data)))
        get_attachments(email.message_from_bytes(data))


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((domainName, domainPort))
securedSocket = ssl.create_default_context().wrap_socket(clientSocket, server_hostname = domainName)
print(securedSocket.recv(BUFFER_SIZE))

print(login(username, password, securedSocket))
print(namespace(securedSocket))
print(list('', '*', securedSocket))
print(select('INBOX', securedSocket))

list_emails(search_value('FROM', 'as', securedSocket))

