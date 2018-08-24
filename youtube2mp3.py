import os
import re
import sys
import logging
import smtplib
import imaplib
import mimetypes
import logging.handlers
    
from email.mime.audio import MIMEAudio
from email.MIMEMultipart import MIMEMultipart

class Logging(object):
    def log(self,level,message):
        comm = re.search("(WARN|INFO|ERROR)", str(level), re.M)
        if comm is None:
            print(level + " is not a level. Use: WARN, ERROR, or INFO!")
            return
        try:
            handler = logging.handlers.WatchedFileHandler(
                os.environ.get("LOGFILE","/var/log/youtube2mp3.log"))
            formatter = logging.Formatter(logging.BASIC_FORMAT)
            handler.setFormatter(formatter)
            root = logging.getLogger()
            root.setLevel(os.environ.get("LOGLEVEL", str(level)))
            root.addHandler(handler)
            logging.exception("(" + str(level) + ") " + "ImageCapture - " + str(message))
            print("(" + str(level) + ") " + "ImageCapture - " + str(message))
        except Exception as e:
            print("Error in Logging class => " + str(e))
            pass
        return
    
class Youtube2mp3(Logging):

    def __init__(self):
        super(Youtube2mp3, self).__init__()
        self.parse_email()        

    def song_name(self,url):
        mp3 = os.popen("/usr/bin/youtube-dl --no-part "
            + str(url)
            + " --restrict-filenames --audio-format mp3"
            + " --get-filename -o \"%(artist)s-%(title)s.%(ext)s\"").read().splitlines()[0]
        return '/home/anthony/Music/' + re.sub('\.[a-z0-9]{3,5}$', '.mp3', str(mp3))
    
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
            self.log("INFO", "Sent email successfully!")
        except smtplib.SMTPAuthenticationError:
            self.log("ERROR", "Could not athenticate with password and username!")
        except Exception as e:
                self.log("ERROR", "Unexpected error in send_mail() error e => " + str(e))
    
    def white_list(self,subject):
        with open('whitelist.txt') as f:
            for name in f.read().splitlines():
                allowed = re.search(str(name), str(subject), re.M | re.I)
                if allowed is not None:
                    self.log("INFO", str(allowed.group()) + " is in the whitelist.")
                    return True
        self.log("WARN", "You do not have permission to convert this video!")
        return False
    
    def convert_video(self,url,sendto):
        self.log("INFO", "Converting video now!")
        os.system("/usr/bin/youtube-dl --no-part "
            + str(url)
            + " --restrict-filenames --extract-audio"
            + " --audio-format mp3 -o \"/home/anthony/Music/%(artist)s-%(title)s.%(ext)s\"")
        self.log("INFO", "Sending song via E-mail.")
        self.send_mail('sshmonitorapp@gmail.com',
            sendto,
            'hkeyscwhgxjzafvj',
            587,'song','converted song attached',
            self.song_name(url))
        sys.exit(0)
    
    def parse_email(self):
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
                    self.logger("INFO", "data: " + str(data[0][1]))
                    mail.store(eid,'+FLAGS','\Deleted')
                    if message is not None and message is not None and subject is not None:
                        if self.white_list(subject.group(2)):
                            self.convert_video(message.group(),re.sub('[<>]','',str(sender.group(3))))
                mail.expunge()
    
        except Exception as e:
            self.log("ERROR", "Exception e => " + str(e))
    
if __name__ == '__main__':
    Youtube2mp3()
