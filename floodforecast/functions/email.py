import email.message as message
import smtplib
from datetime import datetime, timedelta
from ..databases.rainstation_database import _email
from ..databases.rainstation_database import _stationData
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import os


class Email:
    def __init__(self, prjPath, nowFormat, warningStation):
        self.prjPath = prjPath
        self.nowFormat = nowFormat
        self.warningStation = warningStation
        self.sendEmail()

    def sendEmail(self):
        if datetime.now().hour == 16:
            self.mkEmail()
        elif not self.warningStation:
            pass
        else:
            self.mkEmail()

    def mkEmail(self):

        receiver = _email[0:]           # rainstation_database._email裡面的所有收件人
        sender = 'hetengwra9@gmail.com'
        username = 'hetengwra9@gmail.com'
        password = 'heteng85219296'
        smtpserver = 'smtp.gmail.com'      # 發件人郵箱的SMTP服務器

        with open("rainfallWarn.txt", mode='r', encoding='utf-8') as rain_file:
            data = rain_file.read()

        mail_title = '降雨警報'
        mail_body = data

        # 設定root資訊
        msgRoot = MIMEMultipart('mixed')
        msgRoot['Subject'] = Header(mail_title, 'utf-8')
        msgRoot['From'] = sender
        msgRoot['To'] = ", ".join(receiver)
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        # 設定純文字資訊
        msgText = MIMEText(mail_body, 'plain', 'utf-8')
        msgAlternative.attach(msgText)

        # 設定內建圖片資訊
        if not self.warningStation:
            pass
        else:
            rainImagePath = os.path.join(
                self.prjPath, 'images', self.nowFormat
            )

            allFileList = [
                stcode + '-' + _stationData[stcode]['chineseName'] + '.jpg' for stcode in self.warningStation
            ]
            os.chdir(rainImagePath)  # 更改路徑

            for imgName in allFileList:
                with open(imgName, 'rb') as fp:
                    msgImage = MIMEImage(fp.read())
                    msgImage.add_header(
                        'Content-Disposition', '<image_%s>' % imgName)
                    msgRoot.attach(msgImage)

            os.chdir(self.prjPath)           # 更回原路徑

        # 創建一個連接
        smtp = smtplib.SMTP(smtpserver)
        # 連接發送郵件的服務器
        smtp.connect(smtpserver)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(username, password)                                  # 登錄服務器
        smtp.sendmail(sender, receiver, msgRoot.as_string()
                      )            # 填入郵件的相關信息並發送
        smtp.quit()

        return
