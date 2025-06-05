from pydantic import BaseModel, Field
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
import json

class ContactModel(BaseModel):
    name: str
    email: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # 現在時刻をUTCで設定

def send_email(self):
    # メール送信のロジックをここに実装
    print(f"Sending email to {self.email}...")
    # 実際のメール送信処理を追加する場合は、ここに記述します。
    settings_file = open('settings.json','r')
    settings_data = json.load(settings_file)

    """ メッセージのオブジェクト """
    msg = MIMEText(self.mail_body, "plain", "utf-8")
    msg['Subject'] = self.mail_subject
    msg['From'] = self.mail_from
    msg['To'] = self.mail_to

    # エラーキャッチ
    try:
        """ SMTPメールサーバーに接続 """
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)  # SMTPオブジェクトを作成。smtp.gmail.comのSMTPサーバーの587番ポートを設定。
        smtpobj.ehlo()                                 # SMTPサーバとの接続を確立
        smtpobj.starttls()                             # TLS暗号化通信開始
        gmail_addr = settings_data['gmail_addr']       # Googleアカウント(このアドレスをFromにして送られるっぽい)
        app_passwd = settings_data['app_passwd']       # アプリパスワード
        smtpobj.login(gmail_addr, app_passwd)          # SMTPサーバーへログイン

        """ メール送信 """
        smtpobj.sendmail(mail_from, mail_to, msg.as_string())

        """ SMTPサーバーとの接続解除 """
        smtpobj.quit()

    except Exception as e:
        print(e)

    return "メール送信完了"