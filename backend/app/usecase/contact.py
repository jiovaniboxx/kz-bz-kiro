from app.domain.contact import ContactModel
from app.domain.contact import send_email
from app.infrastructure.t_contact_repository import t_contact_repository_save

class ContactUseCase:
    def __init__(self, contact: ContactModel):
        self.contact = contact

    def validate(self):
        # バリデーションを実行
        if not self.contact.name or not self.contact.email or not self.contact.message:
            raise ValueError("全てのフィールドを入力してください。")
        if "@" not in self.contact.email:
            raise ValueError("有効なメールアドレスを入力してください。")
        return True

    def execute(self):
        # ビジネスロジックを実行

        # バリデーションを実行
        print("validating contact...")
        self.validate()

        # データベースに保存
        print(f"Saving contact: {self.contact}")
        t_contact_repository_save(self.contact)

        # メールを送信
        print("Sending email...")
        send_email(self.contact)