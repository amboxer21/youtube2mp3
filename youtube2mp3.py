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
    
class Youtube2mp3(object):

    def __init__(self):
        self.data_for_converter()        

    def song_name(self):
        mp3 = re.search('(^.*.mp3)', str(os.popen('ls -t | tail -n1').read()), re.M | re.I)
        if mp3 is not None: 
            return str(mp3.group())
    
    def send_mail(self,sender,sendto,password,port,subject,body,file_name):
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
            mail.sendmail(sender, sendto, message.as_string())
            print("(INFO) Sent email successfully!")
        except smtplib.SMTPAuthenticationError:
            print("(ERROR) Could not athenticate with password and username!")
        except Exception as e:
                print("(ERROR) Unexpected error in send_mail() error e => " + str(e))
    
    def white_list(self,subject):
        with open('whitelist.txt') as f:
            for name in f.read().splitlines():
                allowed = re.search(str(name), str(subject), re.M | re.I)
                if allowed is not None:
                    print("(INFO) " +str(allowed.group()) + " is in the whitelist.")
                    return True
        print("You do not have permission to convert this video!")
        return False
    
    def convert_video(self,url,sendto):
        print("Converting video now!")
        os.system("/usr/bin/youtube-dl "
            + str(url)
            + " -x --audio-format mp3 -o \"%(artist)s - %(title)s.%(ext)s\"")
        print("(INFO) Sending song via E-mail.")
        self.send_mail('sshmonitorapp@gmail.com',
            sendto,
            'hkeyscwhgxjzafvj',
            587,'song','converted song attached',
            self.song_name())
        sys.exit(0)
    
    def data_for_converter(self):
        try:
            mail = imaplib.IMAP4_SSL('smtp.gmail.com')
            mail.login('sshmonitorapp@gmail.com','hkeyscwhgxjzafvj')
            mail.select('inbox')
    
            (code, data) = mail.search(None, '(UNSEEN)')
            if code == 'OK':
                for eid in data[0].split(' '):
                    (typ, body) = mail.fetch(eid, '(BODY[TEXT])' )
                    (typ, data) = mail.fetch(eid, '(RFC822)' )
                    sender  = re.search('(^From: )(.*)(\<.*\>)', str(data[0][1]), re.M | re.I)
                    subject = re.search('(^Subject: )(.*)', str(data[0][1]), re.M | re.I)
                    message = re.search('(https://(|www\.)youtu(\.be|be)(|\.com)\/(watch\?[\&\=a-z0-9\_\-]+|[\&\=\-\_a-z0-9]+))',
                        str(body[0][1]), re.M | re.I)
                    mail.store(eid,'+FLAGS','\Deleted')
                    if message is not None and message is not None and subject is not None:
                        if self.white_list(subject.group(2)):
                            self.convert_video(message.group(),re.sub('[<>]','',str(sender.group(3))))
                mail.expunge()
    
        except Exception as e:
            print("Exception e => " + str(e))
    
if __name__ == '__main__':
    Youtube2mp3()
