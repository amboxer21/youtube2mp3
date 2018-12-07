import os
import re
import sys
import time
import errno
import logging
import smtplib
import imaplib
import threading
import mimetypes
import subprocess
import logging.handlers
    
from subprocess import Popen
from email.mime.audio import MIMEAudio
from email.MIMEMultipart import MIMEMultipart

class User(object):
    def name(self):
        comm = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()

class FileOpts(User):
    def __init__(self):
        super(FileOpts, self).__init__()
        if not self.file_exists(self.music_directory()):
            if not self.dir_exists(self.root_directory()):
                self.mkdir_p(self.root_directory())
                self.create_file(self.root_directory() + '/youtube2mp3.log')
                self.create_file(self.root_directory() + '/whitelist.txt')
            self.mkdir_p(self.music_directory())

    def root_directory(self):
        return "/home/pi/.youtube2mp3"

    def music_directory(self):
        return str(self.root_directory()) + "/Music"

    def file_exists(self,file_name):
        return os.path.isfile(file_name)

    def create_file(self,file_name):
        if not self.file_exists(file_name):
            open(file_name, 'w')

    def dir_exists(self,dir_path):
        return os.path.isdir(dir_path)

    def mkdir_p(self,dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and self.dir_exists(dir_path):
                pass
            else:
                raise

class Logging(object):
    def log(self,level,message):
        comm = re.search("(WARN|INFO|ERROR)", str(level), re.M)
        try:
            handler = logging.handlers.WatchedFileHandler(
                os.environ.get("LOGFILE","/home/pi/.youtube2mp3/youtube2mp3.log"))
            formatter = logging.Formatter(logging.BASIC_FORMAT)
            handler.setFormatter(formatter)
            root = logging.getLogger()
            root.setLevel(os.environ.get("LOGLEVEL", str(level)))
            root.addHandler(handler)
            # Log all calls to this class in the logfile no matter what.
            if comm is None:
                print(level + " is not a level. Use: WARN, ERROR, or INFO!")
                return
            elif comm.group() == 'ERROR':
                logging.error("(" + str(level) + ") " + "Youtube2Mp3 - " + str(message))
            elif comm.group() == 'INFO':
                logging.info("(" + str(level) + ") " + "Youtube2Mp3 - " + str(message))
            elif comm.group() == 'WARN':
                logging.warn("(" + str(level) + ") " + "Youtube2Mp3 - " + str(message))
            print("(" + str(level) + ") " + "Youtube2Mp3 - " + str(message))
        except IOError as e:
            if re.search('\[Errno 13\] Permission denied:', str(e), re.M | re.I):
                print("(ERROR) Youtube2Mp3 - Must be sudo to run Youtube2Mp3!")
                sys.exit(0)
            print("(ERROR) Youtube2Mp3 - IOError in Logging class => " + str(e))
            logging.error("(ERROR) Youtube2Mp3 - IOError => " + str(e))
        except Exception as e:
            print("(ERROR) Youtube2Mp3 - Exception in Logging class => " + str(e))
            logging.error("(ERROR) Youtube2Mp3 - Exception => " + str(e))
            pass
        return

class Youtube2mp3(Logging,FileOpts):
    def __init__(self):
        super(Youtube2mp3, self).__init__()

    def song_name(self,url):
        mp3 = os.popen("/usr/local/bin/youtube-dl --no-part "
            + str(url)
            + " --restrict-filenames --audio-format mp3"
            + " --get-filename -o \"%(title)s.%(ext)s\"").read().splitlines()[0]
            #+ " --get-filename -o \"%(artist)s-%(title)s.%(ext)s\"").read().splitlines()[0]
        return '/home/pi/.youtube2mp3/Music/' + re.sub('\.[a-z0-9]{3,5}$', '.mp3', str(mp3))
    
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
            mail.quit()
            self.log("INFO", "Sent email successfully!")
        except smtplib.SMTPAuthenticationError:
            self.log("ERROR", "Could not athenticate with password and username!")
        except Exception as e:
                self.log("ERROR", "Unexpected error in send_mail() error e => " + str(e))
    
    def white_list(self,passkey,sender):
        sender = re.sub('[<>]','',str(sender))
        with open('/home/pi/.youtube2mp3/whitelist.txt') as f:
            for name in f.read().splitlines():
                allowed = re.search(str(passkey)+":"+str(sender), str(name), re.M | re.I)
                if allowed is not None:
                    self.log("INFO", str(allowed.group().split(":")[1]) + " is an authorized E-mail!")
                    return True
        self.log("WARN", "You do not have permission to convert this video!")
        self.log("INFO", "KEY => " + str(allowed.group()) + " is NOT unathorized!")
        return False
    
    def convert_video(self,url,sendto):
        song_name = self.song_name(url)
        self.log("INFO", "Converting video now!")
        self.log("INFO", "Song name: " + str(song_name))
        os.system("/usr/local/bin/youtube-dl --no-part "
            + str(url)
            + " --restrict-filenames --extract-audio"
            + " --audio-format mp3 -o "
            + str(song_name))
            #+ " --audio-format mp3 -o \"/home/pi/.youtube2mp3/Music/%(title)s.%(ext)s\"")
            #+ " --audio-format mp3 -o \"/home/pi/.youtube2mp3/Music/%(artist)s-%(title)s.%(ext)s\"")
        self.log("INFO", "Sending song via E-mail.")
        self.send_mail('youtoob2mp3converter@gmail.com',
            re.sub('[<>]','',str(sendto)),
            'etlnqaomfinozxka',
            587,'song','converted song attached',
            str(song_name))
        sys.exit(0)
    
    def parse_email(self):
        try:
            mail = imaplib.IMAP4_SSL('smtp.gmail.com')
            mail.login('youtoob2mp3converter@gmail.com','etlnqaomfinozxka')
            mail.select('inbox')
    
            (code, data) = mail.search(None, '(UNSEEN)')
            if code == 'OK':
                for eid in data[0].split(' '):
                    (typ, body) = mail.fetch(eid, '(BODY[TEXT])' )
                    (typ, data) = mail.fetch(eid, '(RFC822)' )
                    sender  = re.search('(^From: )(.*)(\<.*\>)', str(data[0][1]), re.M | re.I)
                    subject = re.search('(^Subject: )([a-z0-9\-\_]+)', str(data[0][1]), re.M | re.I)
                    message = re.search('(https://(|www\.)youtu(\.be|be)(|\.com)\/(watch\?[\&\=a-z0-9\_\-]+|[\&\=\-\_a-z0-9]+))',
                        str(body[0][1]), re.M | re.I)
                    self.log("INFO", "data: " + str(data[0][1]))
                    mail.store(eid,'+FLAGS','\Deleted')
                    if message is not None and message is not None and subject is not None:
                        if self.white_list(subject.group(2),sender.group(3)):
                            self.convert_video(message.group(),sender.group(3))
                mail.expunge()
        except Exception as e:
            if re.search("FETCH command error: BAD", str(e), re.I):
                #No unread E-mails in their inbox
                pass
            else:
                self.log("ERROR", "Exception e => " + str(e))

class Threading(Youtube2mp3):
    def __init__(self, seconds=1):
        super(Threading, self).__init__()
        self.seconds = seconds
        thread = threading.Thread(target=self.run, args=())
        thread.deamon = True
        thread.start()

    def run(self):
        while True:
            self.parse_email() 
            time.sleep(self.seconds)
    
if __name__ == '__main__':
    Threading()
