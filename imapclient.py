import socket, ssl
import email
import os
from email.header import decode_header
from email.parser import HeaderParser
import tkinter as tk
from tkinter.filedialog import askopenfile

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
    try:
        cmd = "a FETCH " + str(num) + " " + flags + "\r\n" #constructs fetch command
        socket.send(cmd.encode())
        full_msg = b''
        while True:
            msg = securedSocket.recv(BUFFER_SIZE)
            full_msg += msg
            if msg.decode().__contains__("a BAD") or msg.decode().__contains__("a NO"):
                raise PermissionError("Permission denied by server. Error in syntax or something else...")
            if msg.decode().__contains__("a OK FETCH completed"):
                break
        list_msg = full_msg.split(b'\r\n')
        start = list_msg.pop(0)
        end = list_msg.pop()
        data = b'\r\n'.join(list_msg)
        return start, end, data
    except PermissionError as e:
        print(e)
        return None


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
            return True
        else:
            return False


def print_headers(headers):
    print('\r\n')
    for h in headers.items():
        if h[0] == 'Date':
            print("Date: " + h[1])
        if h[0] == 'From':
            print("From " + h[1])
        if h[0] == 'To':
            print("To: " + h[1])
        if h[0] == 'Subject':
            print("Subject: " + h[1])


def list_emails(search_value):
    parser = email.parser.HeaderParser()
    result, data = search_value
    for i in data:  # this loop works only for search command for now
        num = i.decode()
        start, end, data = fetch(num, '(RFC822)', securedSocket)
        headers = parser.parsestr(email.message_from_bytes(data).as_string())
        print_headers(headers)
        print("Body: " + get_body(email.message_from_bytes(data)).decode())
        if(get_attachments(email.message_from_bytes(data))):
            print("Attachments have been placed in " + attachment_dir)


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((domainName, domainPort))
securedSocket = ssl.create_default_context().wrap_socket(clientSocket, server_hostname = domainName)
acknowledgement_message = securedSocket.recv(BUFFER_SIZE) #This can printed

"""
#All of those can be printed to console
login(username, password, securedSocket)
namespace(securedSocket)
list('', '*', securedSocket)
select('INBOX', securedSocket)

#lists all emails with date, from, to, subject headers, body content and attachments
list_emails(search_value('FROM', '', securedSocket))
"""

"""
GUI section ----------------------------------------------------------------------------------
"""


def open_file():
    button_text.set("Clicked")
    file = askopenfile(parent=gui_root, mode='rb', title='Choose a file', filetype=[("Pdf file", "*.pdf")])
    if file:
        print("File was sucessfuly loaded")


gui_root = tk.Tk()

gui_root.wm_title("IMAP client")

canvas = tk.Canvas(gui_root, width=1200, height=600)
canvas.grid(columnspan=3, rowspan=3)

#label
label = tk.Label(gui_root, text="This is an IMAP client", font="Raleway, 18")
label.grid(column=1, row=0)

#button
button_text = tk.StringVar()
#fg - font color, bg - background color
button_button = tk.Button(gui_root, textvariable=button_text, command=lambda:open_file(), font="Raleway, 14", bg="#FEFEFE", fg="#20bebe", height=1, width=15)
button_text.set("Simple Button")
button_button.grid(column=1, row=2)

gui_root.mainloop()