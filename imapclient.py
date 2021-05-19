import socket, ssl
import email
import os
from email.header import decode_header
from email.parser import HeaderParser
import tkinter as tk
from tkinter.filedialog import askopenfile
import shutil

BUFFER_SIZE = 1000000
domainName = "imap.mail.yahoo.com"
domainPort = 993 #993 - IMAP port for safe connections, use 143 for unsecured connections

username = "mifktlab3@yahoo.com"
password = "aguzvnmiqzmjusjr"

project_dir = 'D:\Modesto\VU\Kompiuteriu_tinklai\Lab3\IMAP_client'
attachment_dir = 'D:\Modesto\VU\Kompiuteriu_tinklai\Lab3\IMAP_client\Attachments'
email_dir = 'D:\Modesto\VU\Kompiuteriu_tinklai\Lab3\IMAP_client\Emails'


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


#All of those can be printed to console
login(username, password, securedSocket)
namespace(securedSocket)
#list('', '*', securedSocket)
select('INBOX', securedSocket)
"""
#lists all emails with date, from, to, subject headers, body content and attachments
list_emails(search_value('FROM', '', securedSocket))
"""

"""
GUI section ----------------------------------------------------------------------------------
"""


class Email:
    def __init__(self, h_date, h_from, h_to, h_subject, h_body, h_attachment_msg, full_eml):
        self.h_date = h_date
        self.h_from = h_from
        self.h_to = h_to
        self.h_subject = h_subject
        self.h_body = h_body
        self.h_attachment_msg = h_attachment_msg
        self.full_eml = full_eml
        self.check_var = tk.IntVar()

    def show(self):
        message_window = tk.Tk()

        message_window.wm_title(self.h_subject)
        date_label = tk.Label(message_window, text="Date: " + self.h_date, font="Raleway, 12")
        date_label.grid(row=0, sticky="w")
        from_label = tk.Label(message_window, text="From: " + self.h_from, font="Raleway, 12")
        from_label.grid(row=1, sticky="w")
        to_label = tk.Label(message_window, text="To: " + self.h_to, font="Raleway, 12")
        to_label.grid(row=2, sticky="w")
        subject_label = tk.Label(message_window, text="Subject: " + self.h_subject, font="Raleway, 12")
        subject_label.grid(row=3, sticky="w")
        body_text_anchor = "Body---------------------------------------------------------------------------------------------------"
        body_label = tk.Label(message_window, text=body_text_anchor, font="Raleway, 12")
        body_label.grid(row=4, sticky="w")
        body_box = tk.Text(message_window, height=10, width=60)
        body_box.insert(1.0, self.h_body)
        body_box.grid(row=5, pady=(5, 5))
        if self.h_attachment_msg is not None:
            attachment_label = tk.Label(message_window, text=self.h_attachment_msg, font="Raleway, 9")
            attachment_label.grid(row=6)

        message_window.mainloop()


def open_file():
    file = askopenfile(parent=gui_root, mode='rb', title='Choose a file', filetype=[("Pdf file", "*.pdf")])
    if file:
        print("File was successfully loaded")


def collect_emails(search_value):
    parser = email.parser.HeaderParser()
    result, data = search_value
    collected_emails = []
    for i in data: #this loop only works for search command
        num = i.decode()
        start, end, data = fetch(num, '(RFC822)', securedSocket)
        headers = parser.parsestr(email.message_from_bytes(data).as_string())
        date_text = None
        from_text = None
        to_text = None
        subject_text = None
        attachment_text = None
        for h in headers.items():
            if h[0] == 'Date':
                date_text = str(h[1])
            if h[0] == 'From':
                from_text = str(h[1])
            if h[0] == 'To':
                to_text = str(h[1])
            if h[0] == 'Subject':
                subject_text = str(h[1])

        if (get_attachments(email.message_from_bytes(data))):
            attachment_text = "Attachments have been placed in " + attachment_dir
        body_text = get_body(email.message_from_bytes(data)).decode()
        full_eml = data
        email_obj = Email(date_text, from_text, to_text, subject_text, body_text, attachment_text, full_eml)
        collected_emails.append(email_obj)
    return collected_emails


def list_emails_to_gui(emails):
    for e in emails:
        columns, rows = gui_root.grid_size()
        checkbox = tk.Checkbutton(gui_root, variable=e.check_var)
        checkbox.grid(column=0, row=rows, padx=(20, 20))
        label = tk.Label(gui_root, text=e.h_subject, font="Raleway 12")
        label.grid(column=1, row=rows, padx=(20, 20))
        label = tk.Label(gui_root, text=e.h_date, font="Raleway 12")
        label.grid(column=2, row=rows, padx=(20, 20))
        button = tk.Button(gui_root, text='View Message', command=e.show, font="Raleway, 14", bg="#FEFEFE", fg="#20bebe", height=1, width=15)
        button.grid(column=3, row=rows, padx=(20, 20))


def download_checked():
    for e in emails:
        if e.check_var.get() == 1:
            filename = '%s.eml' % os.path.join(email_dir, e.h_subject)
            with open(filename, 'wb') as fd:
                fd.write(e.full_eml)
    shutil.make_archive('emails', 'zip', email_dir)
    for file in os.listdir(email_dir):
        os.remove(os.path.join(email_dir, file))
    columns, rows = gui_root.grid_size()
    label = tk.Label(gui_root, text='Emails were packed in: ' + project_dir, font="Raleway, 11")
    label.grid(column=0, columnspan=3, sticky="w", row=rows, padx=(20, 20))


def place_download_button():
    columns, rows = gui_root.grid_size()
    button = tk.Button(gui_root, text='Download Checked Messages', command=download_checked, font="Raleway, 14", bg="#fefefe", fg="#20bebe", height=1, width=30)
    button.grid(column=0, columnspan=2, row=rows, padx=(20, 20))

gui_root = tk.Tk()
gui_root.wm_title("IMAP client")
#gui_root.wm_grid(baseWidth=1200, baseHeight=600, widthInc=1200, heightInc=600)

#label
label = tk.Label(gui_root, text="IMAP client", font="Raleway, 18")
label.grid(column=1, row=0, pady=(10, 20))

emails = collect_emails(search_value('FROM', '', securedSocket))
list_emails_to_gui(emails)
place_download_button()

gui_root.mainloop()