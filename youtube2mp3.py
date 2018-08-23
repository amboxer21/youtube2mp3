import os
import re
import sys
import smtplib
import imaplib
import mimetypes


from email import encoders
from email.mime.audio import MIMEAudio

from subprocess import call
from email.MIMEMultipart import MIMEMultipart

def song_name():
    mp3 = re.search('(^.*.mp3)', str(os.popen('ls -t | tail -n1').read()), re.M | re.I)
    if mp3 is not None: 
        return str(mp3.group())

def send_mail(sender,to,password,port,subject,body,file_name):
    try:
        message = MIMEMultipart()
        message['Body'] = body
        message['Subject'] = subject
        audio = MIMEAudio(open(str(file_name), 'rb').read(), 'mp3')
        audio.add_header('Content-Disposition', 'attachment', filename=file_name)
        message.attach(audio)
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.starttls()
        mail.login(sender,password)
        mail.sendmail(sender, to, message.as_string())
        print("(INFO) Sent email successfully!")
    except smtplib.SMTPAuthenticationError:
        print("(ERROR) Could not athenticate with password and username!")
    except Exception as e:
            print("(ERROR) Unexpected error in send_mail() error e => " + str(e))

def white_list(subject):
    with open('whitelist.txt') as f:
        for name in f.read().splitlines():
            print("subject => " + str(subject))
            print "name => " + str(name)
            allowed = re.search(str(name), str(subject), re.M | re.I)
            if allowed is not None:
                print " -> ALLOWED: " + str(allowed.group())
                return True
            print("You do not have permission to convert this video!")

def convert_video(url):
    print("Converting video now!")
    os.system("/usr/bin/youtube-dl " + str(url) + " -x --audio-format mp3 -o \"%(artist)s - %(title)s.%(ext)s\"")
    print("(INFO) Sending song via E-mail.")
    send_mail('sshmonitorapp@gmail.com','sshmonitorapp@gmail.com','hkeyscwhgxjzafvj',587,'song','converted song attached',song_name())
    sys.exit(0)

def data_for_converter():
    try:
        mail = imaplib.IMAP4_SSL('smtp.gmail.com')
        mail.login('sshmonitorapp@gmail.com','hkeyscwhgxjzafvj')
        mail.select('inbox')

        typ, data = mail.search(None, 'ALL')

        for eid in range(int(data[0].split()[-1]), int(data[0].split()[0]), -1):
            typ, body = mail.fetch(eid, '(BODY[TEXT])' )
            typ, data = mail.fetch(eid, '(RFC822)' )
            sender  = re.search('(^From: )(.*)', str(data[0][1]), re.M | re.I)
            subject = re.search('(^Subject: )(.*)', str(data[0][1]), re.M | re.I)
            message = re.search('(https://(|www\.)youtu(\.be|be)(|\.com)\/(watch\?[\&\=a-z0-9\_\-]+|[\&\=\-\_a-z0-9]+))',
                str(body[0][1]), re.M | re.I)
            if message is not None and message is not None and subject is not None:
                print("afsgt")
                if white_list(subject.group(2)):
                    convert_video(message.group())

    except Exception, e:
        print str(e)

if __name__ == '__main__':
    data_for_converter()
