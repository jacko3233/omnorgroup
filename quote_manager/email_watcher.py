import imaplib
import email
import os
from typing import List

from .database import SessionLocal
from .models import QuoteRequest, Attachment


def watch_inbox():
    """Check the IMAP inbox for unseen messages and store them."""
    host = os.environ.get('IMAP_HOST')
    user = os.environ.get('IMAP_USER')
    password = os.environ.get('IMAP_PASS')
    if not all([host, user, password]):
        raise RuntimeError('IMAP credentials not set')

    mail = imaplib.IMAP4_SSL(host)
    mail.login(user, password)
    mail.select('inbox')
    status, messages = mail.search(None, '(UNSEEN)')

    session = SessionLocal()
    attach_dir = 'attachments'
    os.makedirs(attach_dir, exist_ok=True)

    for num in messages[0].split():
        status, msg_data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        sender = msg.get('From')
        subject = msg.get('Subject')
        body = ''
        files: List[Attachment] = []
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get('Content-Disposition'))
                if ctype == 'text/plain' and 'attachment' not in disp:
                    body = part.get_payload(decode=True).decode(errors='ignore')
                elif 'attachment' in disp:
                    filename = part.get_filename()
                    if filename:
                        path = os.path.join(attach_dir, filename)
                        with open(path, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        files.append((filename, path))
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')

        qr = QuoteRequest(sender=sender, subject=subject, body=body)
        session.add(qr)
        session.flush()
        for fn, path in files:
            session.add(Attachment(filename=fn, path=path, quote_request_id=qr.id))
        session.commit()
        mail.store(num, '+FLAGS', '\\Seen')

    session.close()
    mail.logout()
