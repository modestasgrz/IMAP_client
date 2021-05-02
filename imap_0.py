import imaplib
import email
import os

user = 'mifktlab3@yahoo.com'
password = 'aguzvnmiqzmjusjr'

imap_url = 'imap.mail.yahoo.com'

attachment_dir = 'D:\Modesto\VU\Kompiuteriu_tinklai\Lab3\IMAP\Attachments'

def authenticate(user, password, imap_url):
    connection = imaplib.IMAP4_SSL(imap_url)
    connection.login(user, password)
    return connection

def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def search(key, value, connection):
    result, data = connection.search(None, key, '"{}"'.format(value))
    return data

def get_emails(result_bytes):
    msgs = []
    for num in result_bytes[0].split():
        typ, data = connection.fetch(num, '(RFC822)')
        msgs.append(data)
    return msgs

def get_bodies(msgs):
    for msg in msgs:
        print(get_body(email.message_from_bytes(msg[0][1]))) #cyphers out something

def get_attachments(msg):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()

        if bool(fileName): #if attachment == False, the attachment isn't there
            filePath = os.path.join(attachment_dir, fileName)
            with open(filePath, 'wb') as f:
                f.write(part.get_payload(decode=True))


connection = authenticate(user, password, imap_url)
connection.select('INBOX')

get_bodies(get_emails(search('FROM', 'as', connection)))
print(search('FROM', 'as', connection))

result, data = connection.fetch('2', '(RFC822)')
#print(email.message_from_bytes(data[0][1]))
print(get_body(email.message_from_bytes(data[0][1])))
get_attachments(email.message_from_bytes(data[0][1]))