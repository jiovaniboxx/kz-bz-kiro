from pydantic import BaseModel, Field
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
import json
import traceback
import os

class ContactModel(BaseModel):
    name: str
    email: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # 現在時刻をUTCで設定

def send_email(self):
    try:
        print(f"Sending email to {self.email}...")
        base_dir = os.path.dirname(__file__)
        settings_path = os.path.join(base_dir, "settings.json")
        template_path = os.path.join(base_dir, "mail_template.txt")  # ←拡張子を.txtに

        with open(settings_path, 'r') as settings_file:
            settings_data = json.load(settings_file)

        # テンプレートを読み込み、self.nameやself.messageを埋め込む
        with open(template_path, 'r', encoding='utf-8') as tpl_file:
            template = tpl_file.read()
        body = template.format(
            name=self.name,
            email=self.email,
            message=self.message,
            created_at=self.created_at
        )

        msg = MIMEText(body, "plain", "utf-8")
        msg['Subject'] = "お問い合わせ受付しました"
        msg['From'] = "kz-bz-eng-no-reply"
        msg['To'] = self.email

        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpobj.set_debuglevel(True)
        smtpobj.ehlo()
        smtpobj.starttls()
        gmail_addr = settings_data['gmail_addr']
        app_passwd = settings_data['app_passwd']
        smtpobj.login(gmail_addr, app_passwd)

        smtpobj.sendmail(msg['From'], [msg['To']], msg.as_string())
        smtpobj.quit()

    except Exception as e:
        print("メール送信エラー:", e)
        traceback.print_exc()

    return "メール送信完了"