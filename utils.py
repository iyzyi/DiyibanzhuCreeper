import subprocess, sys, datetime
import smtplib
from email.mime.text import MIMEText
import config


def send_email(subject, content):
    if config.email['from'] == "" or config.email['to'] == "" or config.email['code'] == "":
        return

    now = datetime.datetime.now()
    strftime = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f'[{strftime}]')

    msg = MIMEText(content)
    msg["Subject"] = f'[{strftime}] {subject}'
    msg["From"]    = config.email['from']
    msg["To"]      = config.email['to']
    try:
        s = smtplib.SMTP_SSL("smtp.163.com", 465)
        s.login(config.email['from'], config.email['code'])
        s.sendmail(config.email['from'], config.email['to'], msg.as_string())
        s.quit()
        print ("Send Email Success!")
    except smtplib.SMTPException:
        print('Send Email Falied!')