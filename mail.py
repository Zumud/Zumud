import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

from envs import GMAIL_APP_PASSWORD

def send_mail(send_from = "noreply@example.com", send_to=["noreply@example.com"], subject="TestTailoredCV", text="This is a test email!", files=None, server="smtp.gmail.com", port=465):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    with smtplib.SMTP_SSL(server, port) as smtp_server:
        smtp_server.login(user=send_from, password=GMAIL_APP_PASSWORD)
        smtp_server.sendmail(send_from, send_to, msg.as_string())
   